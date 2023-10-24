import simplejson as json
from src.service_layer.utils import handle_error, make_response
from src.config import TEST_MATCHER
from src.uof import PostgresUnitOfWork
import src.exceptions as exceptions
import aiohttp
from datetime import datetime
import logging
import json

logger = logging.getLogger("backend-matcher")


async def start_task(uof: PostgresUnitOfWork, **kwargs):
    """
    Create task_id and corresponding run_ids for sport types

    :param uof:
    :param kwargs: {source1_id, source2_id, started_at, sport_ids: dict[sport_id: {source1_id: list, source2_id: list}],
                    referent_task}
    :return: {task_id: int, run_ids: Dict[sport_id: run_id] }
    """
    async with uof:
        try:
            await uof.begin()
            num_sports = len(kwargs.get('sport_ids'))
            data = {
                'source1_id': kwargs.get('source1_id'),
                'source2_id': kwargs.get('source2_id'),
                'started_at': datetime.strptime(kwargs.get('started_at'), "%Y-%m-%d %H:%M:%S"),
                'finished_at': None,
                'num_sports': num_sports,
                'status_user': 1,
                'status_observer': 1,
                'referent_task': kwargs.get('referent_task')
            }
            new_task_id = await uof.task_repo.create(**data)
            run_ids = {}
            data = {'task_id': new_task_id}

            for sport_id, events in kwargs.get('sport_ids').items():
                data['sport_id'] = int(sport_id)
                data['num_matches'] = None
                data['status_user'] = 1
                data['status_observer'] = 1
                data['runtime'] = None
                events1_string = json.dumps(events.get(str(kwargs.get('source1_id'))))
                events2_string = json.dumps(events.get(str(kwargs.get('source2_id'))))
                data['source1_data'] = events1_string
                data['source2_data'] = events2_string
                new_run_id = await uof.run_repo.create(**data)
                run_ids[sport_id] = new_run_id
            result = {'task_id': new_task_id, 'run_ids': run_ids}
            await uof.commit()
            logger.info(f'New task={new_task_id} created - OK')
            return make_response(result=result)
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error("Given parameters are invalid.")
            return make_response(status_code=404,
                                 detail="Given parameters are invalid.")
        except KeyError:
            await uof.rollback()
            logger.error(f"Given parameters are missing some value.")
            return make_response(status_code=404,
                                 detail="Given parameters are missing some value.")
        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            return make_response(status_code=500,
                                 detail=f"Something went wrong:\n{e}")


async def get_tasks_by_sources(uof: PostgresUnitOfWork, source1_id: int, source2_id: int):
    """

    :param uof:
    :param source1_id:
    :param source2_id:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            tasks = await uof.task_repo.get_by_sources(source1_id, source2_id)
            result = [
                {
                    "task_id": task_id,
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "status_user": status_user,
                    "status_observer": status_observer,
                    "referent_task": referent_task,
                    "source1_id": source1_id_result,
                    "source2_id": source2_id_result,
                    "num_matches": num_matches,
                    "source1_count": source1_count,
                    "source2_count": source2_count,
                }
                for task_id, started_at, finished_at, status_user, status_observer, referent_task,
                source1_id_result, source2_id_result, num_matches, source1_count, source2_count in tasks
            ]
            await uof.commit()
            logger.info(f'{len(tasks)} tasks for sources {source1_id} & {source2_id} was retrieved - OK')
            return make_response(result=result)
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error(f"Given parameters are invalid.")
            return make_response(status_code=404, detail="Given parameters are invalid.")
        except KeyError:
            await uof.rollback()
            logger.error("Given parameters are missing some value.")
            return make_response(status_code=404, detail="Given parameters are missing some value.")
        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            return make_response(status_code=500, detail=f"Something went wrong:\n{e}")


async def run_test_task(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :param request: {
         task_id: int,
         source1_id: int,
         source2_id: int,
         source1_data: List[json],
         source2_data: List[json],
         parameters: Dict[]
    }
    :response:{
        source1_id: int,
        source2_id: int
        task_id: int
        source1_data: List[json],
        source2_data: List[json]
        parameters: Dict[...]
    }
    """
    async with uof:
        try:
            await uof.begin()
            if not (kwargs.get('parameters', None) and kwargs.get('task_id', None)
                    and kwargs.get('source1_id', None) and kwargs.get('source2_id', None)):
                raise exceptions.InvalidParameters()
            _ = await uof.task_repo.get_by_id(kwargs.get('task_id'))
            tasks = await uof.run_repo.get_source_data_by_task_id(kwargs.get('task_id'))

            results_data1 = kwargs.get('source1_data', None)
            results_data2 = kwargs.get('source2_data', None)

            if not (results_data1 or results_data2):
                results_data1 = []
                results_data2 = []
                for source_data1, source_data2 in tasks:
                    for event1 in json.loads(source_data1):
                        results_data1.append(event1)
                    for event2 in json.loads(source_data2):
                        results_data2.append(event2)

            test_data = {
                'referent_task_id': kwargs.get('task_id'),
                'source1_id': kwargs.get('source1_id'),
                'source2_id': kwargs.get('source2_id'),
                'source1_data': results_data1,
                'source2_data': results_data2,
                'parameters': kwargs.get('parameters')
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(TEST_MATCHER + '/match_data/', json=test_data) as resp:
                    if resp.ok:
                        data = {
                            'id': kwargs.get('task_id'),
                            'status_observer': 2
                        }
                        _ = await uof.task_repo.modify(**data)
                        await uof.commit()
                        logger.info(f"Request to test matcher for debug task={kwargs.get('task_id')} - OK")
                        return make_response(result=(await resp.json()).get('task_id'))
                    else:
                        logger.error(f'Request to test matcher failed! {resp.reason}')
                        return make_response(status_code=500, detail=f'Request to test matcher failed! {resp.reason}')

        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error("Given parameters are invalid!")
            return make_response(status_code=404, detail="Given parameters are invalid!")
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"Task id: {kwargs.get('task_id')} dose not exist.")
            return make_response(status_code=404, detail=f"Task id: {kwargs.get('task_id')} dose not exist.")
        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            return make_response(status_code=500, detail=f"Something went wrong:\n{e}")


async def run_revers_match(uof: PostgresUnitOfWork, data, all_results=False):
    """
    :param uof:
    :param request Optional
    ...
    """
    async with uof:
        try:
            await uof.begin()

            # Берем json из файла, если он не пришел запросом
            if not data:
                with open('temp_revers.json', 'r') as file:
                    data = json.load(file)
            result = {}
            for sport in data.keys:
                if len(data[sport]) > 100:
                    request_data = data[sport][:100]
                else:
                    request_data = data[sport]
                async with aiohttp.ClientSession() as session:
                    logger.info(f"Data for quality check has been sent to test matcher")
                    async with session.post(TEST_MATCHER + '/revers_match/', json=request_data) as resp:
                        if resp.ok:
                            logger.info(f"Result data from test matcher successfully received")
                            response_data = await resp.json()
                            await uof.commit()
                            result[sport] = response_data
                            logger.info(f"Result data from test matcher successfully processed")
                        else:
                            logger.error(f'Request to test matcher failed! {resp.reason}')
                            return make_response(status_code=500, detail=f'Request to test matcher failed! {resp.reason}')

            return make_response(result=result)
        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            return make_response(status_code=500, detail=f"Something went wrong:\n{e}")


