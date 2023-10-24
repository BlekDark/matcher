from src.uof import PostgresUnitOfWork
import src.exceptions as exceptions
import logging
import simplejson as json
from datetime import datetime
logger = logging.getLogger("backend-matcher")


async def finish_run(uof: PostgresUnitOfWork, **kwargs):
    """

    :param uof:
    :param kwargs:
    {
       run_id: int,
       task_id: int,
       num_matches: int,
       runtime: float,
       pairs: List[dict],
       updated_at: timestamp
    }
    :return:
    """
    response = {'status_code': 200, 'detail': "OK"}
    async with uof:
        try:
            await uof.begin()
            data = {'id': kwargs.get('run_id'),
                    'runtime': kwargs.get('runtime'),
                    'num_matches': kwargs.get('num_matches')}
            success = await uof.run_repo.modify(**data)
            if not success:
                logger.warning(f"Somehow it did not crash, but NOT modified run={kwargs.get('run_id')}")
            for events_result in kwargs.get('pairs'):
                event1 = events_result.get('event1')
                event2 = events_result.get('event2')
                overall_similarity = events_result.get('overall_similarity')
                teams_similarity = events_result.get('teams_similarity')
                league_similarity = events_result.get('league_similarity')
                is_swapped = events_result.get('is_swapped')
                event1_string = json.dumps(event1, ignore_nan=True)
                event2_string = json.dumps(event2, ignore_nan=True)
                data = {'run_id': kwargs.get('run_id'),
                        'event1': event1_string,
                        'event2': event2_string,
                        'is_match': True,
                        'is_uncertain': False,
                        'updated_at': datetime.strptime(kwargs.get('updated_at'), "%Y-%m-%d %H:%M:%S"),
                        'modified_by': None,
                        'mismatch': None,
                        'overall_similarity': overall_similarity,
                        'teams_similarity': teams_similarity,
                        'league_similarity': league_similarity,
                        'is_swapped': is_swapped
                        }
                _ = await uof.result_repo.create(**data)
            await uof.commit()
            logger.info(f"{len(kwargs.get('pairs'))} results of run_id={kwargs.get('run_id')} successfully stored.")

            # here check if task is done
            done_runs = await uof.run_repo.get_num_done_runs(task_id=kwargs.get('task_id'))
            num_runs = await uof.task_repo.get_num_sports(task_id=kwargs.get('task_id'))
            if done_runs == num_runs:
                # the task is done
                data = {'id': kwargs.get('task_id'),
                        'finished_at': datetime.strptime(kwargs.get('updated_at'), "%Y-%m-%d %H:%M:%S")}
                success = await uof.task_repo.modify(**data)
                if not success:
                    logger.warning(f"Somehow it did not crash, but NOT modified task={kwargs.get('task_id')}")
                else:
                    logger.info(f"Task={kwargs.get('task_id')} successfully finished.")
            await uof.commit()

            response['result'] = 'OK'
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error(f"Given parameters are invalid.")
            response['status_code'] = 404
            response['detail'] = f"Given parameters are invalid."
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"The run={kwargs.get('run_id')} does not exist in db.")
            response['status_code'] = 404
            response['detail'] = f"The run={kwargs.get('run_id')} does not exist in db."
        except KeyError:
            await uof.rollback()
            logger.error(f"Given parameters are missing some value.")
            response['status_code'] = 404
            response['detail'] = f"Given parameters are missing some value."
        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            response['status_code'] = 500
            response['detail'] = f"Something went wrong:\n{e}"
    return response
