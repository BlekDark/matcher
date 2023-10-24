import requests
from typing import Tuple, Optional, List
import pandas as pd
from collections import defaultdict
import traceback
import logging
logger = logging.getLogger("event-matcher")


def get_data(source1: Tuple[int, str], source2: Tuple[int, str],
             rawdata1: Optional[List[dict]] = None, rawdata2: Optional[List[dict]] = None):
    """

    :param source1: (source_id, source_url)
    :param source2: (source_id, source_url)
    :param rawdata1:
    :param rawdata2:
    :return:
    """
    data = defaultdict(dict)
    data = defaultdict(lambda: defaultdict(dict))
    try:
        if rawdata1 is not None and rawdata2 is not None:
            # data1 = pd.DataFrame.from_records(rawdata1).groupby("sport")
            # data2 = pd.DataFrame.from_records(rawdata2).groupby("sport")
            if len(rawdata1) == 0 or len(rawdata2) == 0:
                logger.info('There is no data from one of bk')
                return data, (False, 'There is no data from one of bk')
            data1 = pd.DataFrame.from_records(rawdata1)
            data2 = pd.DataFrame.from_records(rawdata2)
            if "is_cyber" in data1.columns:
                data1['is_cyber'] = data1['is_cyber'].astype(str)
            if "is_cyber" in data2.columns:
                data2['is_cyber'] = data2['is_cyber'].astype(str)
        else:
            response1 = requests.get(source1[1])
            response2 = requests.get(source2[1])
            if not (response1.ok and response2.ok):
                reason = response1.reason if response1.ok else response2.reason
                return {}, (False, reason)
            # data1 = pd.DataFrame.from_records(response1.json()).groupby("sport")
            # data2 = pd.DataFrame.from_records(response2.json()).groupby("sport")
            data1 = pd.DataFrame.from_records(response1.json())
            data2 = pd.DataFrame.from_records(response2.json())
        if "is_cyber" not in data1.columns:
            data1.loc[:, "is_cyber"] = "0"
        else:
            data1["is_cyber"].fillna("0", inplace=True)
        if "is_cyber" not in data2.columns:
            data2.loc[:, "is_cyber"] = "0"
        else:
            data2["is_cyber"].fillna("0", inplace=True)
        data1 = data1.groupby(["sport", "is_cyber"])
        data2 = data2.groupby(["sport", "is_cyber"])
        common_sports = data1.groups.keys() & data2.groups.keys()
        for (sport, is_cyber), events1 in data1:
            if (sport, is_cyber) in common_sports:
                data[sport][is_cyber][source1[0]] = events1.to_dict('records')
        for (sport, is_cyber), events2 in data2:
            if (sport, is_cyber) in common_sports:
                data[sport][is_cyber][source2[0]] = events2.to_dict('records')
        return data, (True, 'OK')
    except Exception as e:
        traceback.print_exc()
        return data, (False, str(e))


def get_data_from_custom_json(rawdata1: Optional[List[dict]] = None, rawdata2: Optional[List[dict]] = None):
    """
    :param rawdata1:
    :param rawdata2:
    :return:
    """
    data = defaultdict(dict)
    data = defaultdict(lambda: defaultdict(dict))
    try:
        if len(rawdata1) == 0 or len(rawdata2) == 0:
            logger.info('There is no data from one of bk')
            return data, (False, 'There is no data from one of bk')
        data1 = pd.DataFrame.from_records(rawdata1)
        data2 = pd.DataFrame.from_records(rawdata2)
        if "is_cyber" in data1.columns:
            data1['is_cyber'] = data1['is_cyber'].astype(str)
        if "is_cyber" in data2.columns:
            data2['is_cyber'] = data2['is_cyber'].astype(str)

        if "is_cyber" not in data1.columns:
            data1.loc[:, "is_cyber"] = "0"
        else:
            data1["is_cyber"].fillna("0", inplace=True)
        if "is_cyber" not in data2.columns:
            data2.loc[:, "is_cyber"] = "0"
        else:
            data2["is_cyber"].fillna("0", inplace=True)
        data1 = data1.groupby(["sport", "is_cyber"])
        data2 = data2.groupby(["sport", "is_cyber"])
        common_sports = data1.groups.keys() & data2.groups.keys()
        for (sport, is_cyber), events1 in data1:
            if (sport, is_cyber) in common_sports:
                data[sport][is_cyber]['bk1'] = events1.to_dict('records')
        for (sport, is_cyber), events2 in data2:
            if (sport, is_cyber) in common_sports:
                data[sport][is_cyber]['bk2'] = events2.to_dict('records')
        return data, (True, 'OK')
    except Exception as e:
        traceback.print_exc()
        return data, (False, str(e))


def get_event(source, event_id):
    for event in source:
        if event['bk_event_id'] == event_id:
            return event
    return None


def get_event_for_custom(source, event_id):
    for event in source:
        if event['event_id'] == event_id:
            return event
    return None


def get_report(result, test_source, compared_source):
    report = []
    for compared_id, (test_id, overall_similarity, teams_similarity, league_similarity, is_swapped) in result.items():
        test_event = get_event(test_source, test_id)
        compared_event = get_event(compared_source, compared_id)
        res = {
            "event1": test_event,
            "event2": compared_event,
            "overall_similarity": overall_similarity,
            "teams_similarity": teams_similarity,
            "league_similarity": league_similarity,
            "is_swapped": is_swapped
        }
        report.append(res)
    return report


def get_custom_report(result, test_source, compared_source, sport_name, is_cyber):
    report = []
    for compared_id, (test_id, overall_similarity, teams_similarity, league_similarity, is_swapped) in result.items():
        test_event = get_event_for_custom(test_source, test_id)
        compared_event = get_event_for_custom(compared_source, compared_id)
        res = {
            "event1": test_event,
            "event2": compared_event,
            "overall_similarity": overall_similarity,
            "teams_similarity": teams_similarity,
            "league_similarity": league_similarity,
            "is_swapped": is_swapped,
            "is_match": True,
            "mismatch": False,
            "sport": sport_name,
            "is_cyber": is_cyber
        }
        report.append(res)
    return report

