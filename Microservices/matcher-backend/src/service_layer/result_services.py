from src.uof import PostgresUnitOfWork
from src.service_layer.utils import handle_error,  make_response
import src.exceptions as exceptions
import logging
from datetime import datetime
import simplejson as json

logger = logging.getLogger("backend-matcher")



"""
input
    source1_id
    source2_id
    [started_at, finished_at]
------------------------
output
    [
        {
            task_id: int
            started_at: timestamp
            finished_at: timestamp
            status_user: int
            status_observer: int
            runs: [
                    {
                        run_id: int
                        sport_id: int
                        status_user: int
                        status_observer: int
                        runtime: float
                        results: [{'result_id', 'event1': json1, 'event2': json2, 'is_match', mismatch}]
                        mismatched: {
                                source1_id: [json]
                                source2_id: [json]
                            }
                    }
                ]
        }
    ]
"""


async def get_results(uof: PostgresUnitOfWork, **kwargs):
    """

    :param uof:
    :param kwargs: {source1_id, source2_id, started_at, finished_at}
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            if kwargs.get('task_id', None) is not None:
                tasks = [await uof.task_repo.get_by_id(entry_id=kwargs.get('task_id'))]
            else:
                tasks = await uof.task_repo.get_by_sources(kwargs.get("source1_id"), kwargs.get("source2_id"))
            result = []
            started_at = kwargs.get("started_at", None)
            finished_at = kwargs.get("finished_at", None)

            for task_id, task_started_at, task_finished_at, task_status_user, task_status_observer, task_referent_task,\
                    source1_id, source2_id in tasks:
                # delete by 1000.0 since msec to sec conversion
                if (started_at and finished_at) \
                        and not datetime.fromtimestamp(started_at / 1000.0) <= task_started_at <= datetime.fromtimestamp(finished_at / 1000.0):
                    continue
                res = {'task_id': task_id,
                       'started_at': task_started_at,
                       'finished_at': task_finished_at,
                       'status_user': task_status_user,
                       'status_observer': task_status_observer,
                       'referent_task': task_referent_task}
                runs_data = []
                runs = await uof.run_repo.get_by_task_id(task_id=task_id)
                for run_id, run_sport_id, run_status_user, run_status_observer, run_runtime, run_data1, run_data2 \
                        in runs:
                    
                    if isinstance(run_data1, str):
                        run_data1 = json.loads(run_data1)
                    elif run_data1 is None:
                        run_data1 = []

                    if isinstance(run_data2, str):
                        run_data2 = json.loads(run_data2)
                    elif run_data2 is None:
                        run_data2 = []

                    data1_id2ev = {m.get("bk_event_id"): m for m in run_data1}
                    data2_id2ev = {m.get("bk_event_id"): m for m in run_data2}

                    runs_res = {'run_id': run_id,
                                'sport_id': run_sport_id,
                                'status_user': run_status_user,
                                'status_observer': run_status_observer,
                                'runtime': run_runtime}
                    results = []

                    run_results = await uof.result_repo.get_by_run_id(run_id)
                    for result_id, event1, event2, is_match, mismatch, overall_similarity, teams_similarity, league_similarity, is_swapped in run_results:
                        event1 = json.loads(event1)
                        event2 = json.loads(event2)
                        if event1.get("bk_event_id") in data1_id2ev.keys():
                            data1_id2ev.pop(event1.get("bk_event_id"))
                        elif event1.get("bk_event_id") in data2_id2ev.keys():
                            data2_id2ev.pop(event1.get("bk_event_id"))
                        if event2.get("bk_event_id") in data1_id2ev.keys():
                            data1_id2ev.pop(event2.get("bk_event_id"))
                        elif event2.get("bk_event_id") in data2_id2ev.keys():
                            data2_id2ev.pop(event2.get("bk_event_id"))
                        r = {'result_id': result_id,
                             'event1': event1,
                             'event2': event2,
                             'is_match': is_match,
                             'mismatch': mismatch,
                             'overall_similarity': overall_similarity,
                             'teams_similarity': teams_similarity,
                             'league_similarity': league_similarity,
                             'is_swapped': is_swapped}
                        results.append(r)
                    runs_res['results'] = results
                    runs_res['mismatched'] = {source1_id: list(data1_id2ev.values()),
                                              source2_id: list(data2_id2ev.values())}
                    runs_data.append(runs_res)

                res['runs'] = runs_data
                result.append(res)

            await uof.commit()
            if kwargs.get('task_id', None) is not None:
                logger.info(f'Get results for task {kwargs.get("task_id")}  - OK')
            else:
                logger.info(f'Get results for sources {kwargs.get("source1_id")} & {kwargs.get("source2_id")}  - OK')
            return make_response(result=result)
        except Exception as e:
            await handle_error(uof, e)


async def create_results(uof: PostgresUnitOfWork, **kwargs):
    """
    {run_id: List[res]}, где res
       res = {
                  'event1': json,
                  'event2':json,
                  'is_match': True, (потому что чел вручную нашел пару событий)
                  'mismatch':True  (потому что он ручной, от пользователя)
                 }
    :param uof:
    :param kwargs: {run_id: List[res]}
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            all_created_results = 0
            for run_id, results in kwargs.items():
                added_results = 0
                for res in results:
                    data = {'run_id': int(run_id)}
                    if not res.get('event1', None):
                        raise exceptions.InvalidParameters()
                    data['event1'] = json.dumps(res.get('event1'), ignore_nan=True)
                    if not res.get('event2', None):
                        raise exceptions.InvalidParameters()
                    data['event2'] = json.dumps(res.get('event2'), ignore_nan=True)
                    if 'is_match' not in res.keys():
                        raise exceptions.InvalidParameters()
                    data['is_match'] = res.get('is_match')
                    data['is_uncertain'] = res.get('is_uncertain', None)
                    data['updated_at'] = datetime.now()
                    data['is_uncertain'] = res.get('is_uncertain', None)
                    data['mismatch'] = res.get('mismatch', None)
                    data['overall_similarity'] = res.get('overall_similarity', None)
                    data['teams_similarity'] = res.get('teams_similarity', None)
                    data['league_similarity'] = res.get('league_similarity', None)
                    data['is_swapped'] = res.get('is_swapped', None)
                    new_result_id = await uof.result_repo.create(**data)
                    added_results += 1
                all_created_results += added_results
                logger.info(f"{added_results} new results for run={run_id} were inserted.")
                task_id = await uof.run_repo.get_task(run_id=int(run_id))
                status = 2
                # todo: check if all done --> status = 3
                data = {'id': task_id, 'status_user': status}
                success = await uof.task_repo.modify(**data)
                if not success:
                    logger.warning(f"Something strange in user status modification in task={task_id}")
            await uof.commit()
            logger.info(f"{all_created_results} new results were successfully created.")
            return make_response(detail=f"{all_created_results} new results were successfully created.")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error("Some obligatory parameters are missing!")
            return make_response(404, "Some obligatory parameters are missing!")
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"No entry exists in the database results")
            return make_response(404, "No entry exists in the database results")
        except Exception as e:
            return await handle_error(uof, e)


async def modify_results(uof: PostgresUnitOfWork, **kwargs):
    """
    [  {result_id: int,
    'mismatch':False (потому что этот результат найден системой, но уже просмотрен пользователем.
    'is_match': True/False (в зависимости что нажмет юзер галочку или крестик)
    },
    ...
    ]
    :param uof:
    :param kwargs:  {results: [{result_id: int , ...}]}
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            for res in kwargs.get("results"):
                if not res.get('result_id', None):
                    raise exceptions.InvalidParameters(f'No result_id given!')
                data = {
                    "id": int(res.get('result_id'))}
                if 'is_match' in res.keys():
                    data["is_match"] = res.get('is_match')
                if 'is_uncertain' in res.keys():
                    data["is_uncertain"] = res.get('is_uncertain')
                data["updated_at"] = datetime.now()
                if 'modified_by' in res.keys():
                    data["modified_by"] = res.get('modified_by')
                if 'mismatch' in res.keys():
                    data["mismatch"] = res.get('mismatch')
                success = await uof.result_repo.modify(**data)
                if success:
                    logger.debug(f"Result={res.get('result_id')} was successfully modified.")
                else:
                    logger.warning(f"Result={res.get('result_id')} was not modified and not raised by any exception!")
                task_id = await uof.result_repo.get_task(result_id=int(res.get('result_id')))
                status = 2
                # todo: check if all done --> status = 3
                data = {'id': task_id, 'status_user': status}
                success = await uof.task_repo.modify(**data)
                if not success:
                    logger.warning(f"Something strange in user status modification in task={task_id}")
            await uof.commit()
            logger.info(f"{len(kwargs.get('results'))} results were successfully modified.")
            return make_response(200, f"{len(kwargs.get('results'))} results were successfully modified.")
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"No entry exists in the database results")
            return make_response(404, "No entry exists in the database results")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error(f"Invalid parameters are given.")
            return make_response(404, "Invalid parameters are given.")
        except Exception as e:
            return await handle_error(uof, e)


async def delete_results(uof: PostgresUnitOfWork, **kwargs):
    """

    :param uof:
    :param kwargs: results: [result_id]
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            if not kwargs.get('results', None):
                raise exceptions.InvalidParameters()
            deleted_results = 0
            for result_id in kwargs.get('results'):
                n = await uof.result_repo.delete(**{'id': int(result_id)})
                deleted_results += n
            await uof.commit()
            logger.info(f"{deleted_results} results were successfully deleted from the database.")
            return make_response(200, f"{deleted_results} results were successfully deleted from the database.")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error(f"No results was given in parameters.")
            return make_response(404, "Some id does not exists in the database results")
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"Some id does not exists in the database results")
            return make_response(404, "No results was given in parameters.")
        except Exception as e:
            return await handle_error(uof, e)

async def get_manual_matches(uof: PostgresUnitOfWork):
    def is_manual_duplicates(pair1, pair2):
        pair1_ev1_name, pair1_ev2_name = pair1[7], pair1[8]
        pair2_ev1_name, pair2_ev2_name = pair2[7], pair2[8]
        return (pair1_ev1_name == pair2_ev1_name and pair1_ev2_name == pair2_ev2_name) or \
            (pair1_ev1_name == pair2_ev2_name and pair1_ev2_name == pair2_ev1_name)
    """
    Get whitelist and banlist with manual result matches.
    Format of each entry:
     {
        "event1.team1":str,
        "event1.team2":str,
        "event2.team1":str,
        "event2.team2":str,
        "event1.league":str,
        "event2.league":str,
        "is_swapped": bool
    }
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            raw_whitelist, raw_banlist = await uof.result_repo.get_manual_matches()
            await uof.commit()
            duplicates = []
            for pair_events1 in raw_whitelist:
                for pair_events2 in raw_banlist:
                    if is_manual_duplicates(pair_events1, pair_events2):
                        duplicates.append(pair_events1)
                        break

            for duplicate in duplicates:
                if duplicate in raw_whitelist:
                    raw_whitelist.remove(duplicate)

            whitelist = [{
                "event1.team1": t1_1,
                "event1.team2": t1_2,
                "event2.team1": t2_1,
                "event2.team2": t2_2,
                "event1.league": l1,
                "event2.league": l2,
                "is_swapped": is_swapped,
                "result_id": res_id} for t1_1, t1_2, l1, t2_1, t2_2, l2, is_swapped, ev1_name, ev2_name, res_id in raw_whitelist]
            banlist =  [{"event1.team1": t1_1,
                        "event1.team2": t1_2,
                        "event2.team1": t2_1,
                        "event2.team2": t2_2,
                        "event1.league": l1,
                        "event2.league": l2,
                        "is_swapped": is_swapped,
                        "result_id": res_id} for t1_1, t1_2, l1, t2_1, t2_2, l2, is_swapped, ev1_name, ev2_name, res_id in raw_banlist]

            result = {'whitelist': whitelist, 'banlist': banlist}
            logger.info(f'Get all manual matches - OK')
            return make_response(result=result)
        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            return make_response(status_code=404, detail=f"Something went wrong:\n{e}")

