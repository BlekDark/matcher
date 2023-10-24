from typing import List, Dict, Tuple
from collections import defaultdict
from config import HOST_BACKEND
import json
import logging
import requests
from datetime import datetime
logger = logging.getLogger("event-matcher")


def trigger_webhook(host: str, data):
    try:
        res = requests.post(host, json=json.dumps(data))
        if not res.ok:
            logger.info(f'Request to webhook host failed!\n{res.reason}')
    except Exception as ex:
        logger.error(f"Something went wrong!\n{ex}")


def get_sources():
    response = requests.get(HOST_BACKEND + '/source')
    if not response.ok:
        raise RuntimeError(f"The request for sources to backend service has failed!\n{response.reason}")
    mes = response.json()
    sources = {}
    for s in mes.get("result"):
        sources[s.get('source_name')] = (s.get('source_id'), s.get('source_url'))
    return sources


def get_sport_types():
    response = requests.get(HOST_BACKEND + '/types')
    if not response.ok:
        raise RuntimeError(f"The request for sport_types to backend service has failed!\n{response.reason}")
    mes = response.json()
    sport_types = defaultdict(lambda: defaultdict(dict))
    for sport_id, sport_name, is_cyber in mes.get("result"):
        sport_types[sport_name][str(is_cyber)] = sport_id
    return sport_types


def add_sport_type(sport_name: str, is_cyber: str):
    """

    :param is_cyber:
    :param sport_name:
    :return: sport_id
    """
    data = {
        'name': sport_name,
        'is_cyber': is_cyber
    }
    response = requests.post(HOST_BACKEND + '/types', json=json.dumps(data))
    if not response.ok:
        raise RuntimeError(f"The request for sport={sport_name} creation has failed!\n{response.reason}")
    result = response.json().get('result')
    return result


def create_task(source1_id: int, source2_id: int, sport_ids: Dict, referent_task: int = None) -> Tuple[int, Dict[str, int]]:
    """

    :param source1_id:
    :param source2_id:
    :param sport_ids: {id: events}
    :return: (task_id, Dict[sport_id: run_id])
    :param referent_task:
    """
    data = {
        'source1_id': source1_id,
        'source2_id': source2_id,
        'started_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'sport_ids': sport_ids,
        'referent_task': referent_task
    }
    response = requests.post(HOST_BACKEND + '/start_task', json=json.dumps(data, default=str))
    if not response.ok:
        raise RuntimeError(f"The request for task creation has failed!\n{response.reason}")
    result = response.json().get('result')
    return result.get('task_id'), result.get('run_ids')


def save_test_matcher_metadata(task_id: int, base_configuration, source1_data, source2_data):
    bk1_event_count = len(source1_data)
    bk2_event_count = len(source2_data)
    all_event_count = bk1_event_count + bk2_event_count

    data = {
        'task_id': task_id,
        'remove_candidate_threshold': base_configuration['REMOVE_CANDIDATE_THRESHOLD'],
        'confident_threshold': base_configuration['CONFIDENT_THRESHOLD'],
        'minimal_sim_threshold': base_configuration['MINIMAL_SIM_THRESHOLD'],
        'final_sim_ratio': base_configuration['FINAL_SIM_RATIO'],
        'bk1_event_count': bk1_event_count,
        'bk2_event_count': bk2_event_count,
        'all_event_count': all_event_count,
    }

    response = requests.post(HOST_BACKEND + '/save_metadata', json=json.dumps(data, default=str))
    if not response.ok:
        raise RuntimeError(f"Test match metadata save has been failed!\n{response.reason}")
    return True


def finish_run(run_id: int, task_id: int, num_matches: int, runtime: float, pairs: List[dict]):
    """

    :param run_id:
    :param task_id:
    :param num_matches:
    :param runtime:
    :param pairs:
    :return: {'OK'}
    """
    data = {
        'run_id': run_id,
        'task_id': task_id,
        'num_matches': num_matches,
        'runtime': runtime,
        'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'pairs': pairs
    }
    response = requests.post(HOST_BACKEND + '/finish_run', json=json.dumps(data, default=str))
    if not response.ok:
        raise RuntimeError(f"The request for run={run_id} completion has failed!\n{response.reason}")
    result = response.json().get('result')
    return result


def get_configuration(source1_id: int, source2_id: int, default: bool = False):
    """

    :param default:
    :param source1_id:
    :param source2_id:
    :return:
    """
    data = {'source1_id': source1_id, 'source2_id': source2_id, 'default': default}
    response = requests.get(HOST_BACKEND + '/config', params=data)
    if not response.ok:
        raise RuntimeError(f"The request for configuration values has failed!\n{response.reason}")
    result = response.json().get('result')
    return result


def get_parameters():
    """
    :return:
    """
    data = {'default': True}
    response = requests.get(HOST_BACKEND + '/config', params=data)
    if not response.ok:
        raise RuntimeError(f"The request for parameter values has failed!\n{response.reason}")
    result = response.json().get('result')
    return result


def get_manual_matches():
    """
    return 2 lists: whitelist and banlist
    {
        "event1.team1":str,
        "event1.team2":str,
        "event2.team1":str,
        "event2.team2":str,
        "event1.league":str,
        "event2.league":str,
        "is_swapped": bool
    }
    :return: List[Dict], List[Dict]
    """
    response = requests.get(HOST_BACKEND + '/manual_matches')
    if not response.ok:
        raise RuntimeError(f"The request for sources to backend service has failed!\n{response.reason}")
    mes = response.json()
    whitelist = mes.get("result").get("whitelist")
    banlist = mes.get("result").get("banlist")
    return whitelist, banlist


def get_task_by_id(task_id):
    response = requests.get(HOST_BACKEND + '/pairs_custom')
    if not response.ok:
        raise RuntimeError(f"The request for pairs_custom to backend service has failed!\n{response.reason}")
    result = response.json()
    return result
