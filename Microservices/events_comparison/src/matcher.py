from src.measure import get_similarity
from src.loader import get_event, get_event_for_custom
from src.utils import preprocess_string
from src.loader import get_report, get_custom_report
from src.transform import transliterate
from config import OUTPUT_TOPIC
from kafka import producer, send_2_rabbit

import json
import logging
from typing import List, Dict
from statistics import mean
import aio_pika
logger = logging.getLogger("event-matcher")

def compute_similarity(transformation, event1, event2):
    event1_token1 = transformation(event1['team1'])
    event1_token2 = transformation(event1['team2'])
    event2_token1 = transformation(event2['team1'])
    event2_token2 = transformation(event2['team2'])

    event1_league = transformation(event1['league_name'])
    event2_league = transformation(event2['league_name'])
    plain_token_similarities = [mean([get_similarity(event1_token1, event2_token1),
                                      get_similarity(event1_token2, event2_token2)])
                                ]
    swapped_token_similarities = [mean([get_similarity(event1_token1, event2_token2),
                                        get_similarity(event1_token2, event2_token1)])
                                  ]

    league_similarities = [get_similarity(event1_league, event2_league)]

    if transformation != preprocess_string:
        # cross-transforms variations
        base_event1_token1 = preprocess_string(event1['team1'])
        base_event1_token2 = preprocess_string(event1['team2'])
        base_event2_token1 = preprocess_string(event2['team1'])
        base_event2_token2 = preprocess_string(event2['team2'])

        base_event1_league = preprocess_string(event1['league_name'])
        base_event2_league = preprocess_string(event2['league_name'])

        plain_token_similarities += [
            mean([get_similarity(event1_token1, base_event2_token1),
                  get_similarity(event1_token2, base_event2_token2)]),
            mean([get_similarity(base_event1_token1, event2_token1),
                  get_similarity(base_event1_token2, event2_token2)]),
        ]

        swapped_token_similarities += [
            mean([get_similarity(event1_token1, base_event2_token2),
                  get_similarity(event1_token2, base_event2_token1)]),
            mean([get_similarity(base_event1_token1, event2_token2),
                  get_similarity(base_event1_token2, event2_token1)]),
        ]
        league_similarities += [
            get_similarity(event1_league, base_event2_league),
            get_similarity(base_event1_league, event2_league)
        ]
    max_plain_token_similarity = max(plain_token_similarities)
    max_swapped_token_similarity = max(swapped_token_similarities)
    is_swapped = max_swapped_token_similarity > max_plain_token_similarity

    return max([max_swapped_token_similarity, max_plain_token_similarity]), max(league_similarities), is_swapped


async def match_event(test_event: Dict, compared_events: List, parameters: Dict[str, float], info: Dict = [], to_output_data: bool = False, custom: bool = False):
    """
    Find the closest event from comparing collection of events for the test_ one
    :param info:
    :param parameters:
    :param test_event:
    :param compared_events:
    :return:
    """
    event_type = test_event['sport']
    max_sim = parameters.get('MINIMAL_SIM_THRESHOLD')
    max_token_sim = -1
    max_league_sim = -1
    is_swapped = None
    closest_event, remove_from_candidates = None, False
    for event in compared_events:
        if event['sport'] != event_type:
            continue

        base_token_sim, base_league_sim, base_is_swapped = compute_similarity(preprocess_string, test_event, event)
        translit_token_sim, translit_league_sim, translit_is_swapped = compute_similarity(transliterate, test_event, event)
        token_sim = max(base_token_sim, translit_token_sim)
        league_sim = max(base_league_sim, translit_league_sim)
        cur_is_swapped = base_is_swapped or translit_is_swapped

        final_sim = token_sim * parameters.get('FINAL_SIM_RATIO') + league_sim * (1 - parameters.get('FINAL_SIM_RATIO'))

        if final_sim > max_sim:
            max_sim = final_sim
            max_token_sim = token_sim
            max_league_sim = league_sim
            is_swapped = cur_is_swapped
            closest_event = event
            if final_sim >= parameters.get('REMOVE_CANDIDATE_THRESHOLD'):
                remove_from_candidates = True
            if final_sim >= parameters.get('CONFIDENT_THRESHOLD') and not custom:
                remove_from_candidates = True
                try:
                    res = {
                        "event1": test_event,
                        "event2": event,
                        "overall_similarity": max_sim,
                        "teams_similarity": max_token_sim,
                        "league_similarity": max_league_sim,
                        "is_swapped": is_swapped
                    }
                    result = {'status_code': 200,
                              'reason': 'Instant match pair',
                              'runtime': 0,
                              'result': [res]}
                    result.update(info)
                    await send_2_rabbit(json.dumps(result), to_output_data=to_output_data)
                except Exception as e:
                    logger.error(f'Error during sending instant match pair: {e}')


    return closest_event, remove_from_candidates, max_sim, max_token_sim, max_league_sim, is_swapped


async def recursed_match(result, event, test_source, compared_source, parameters, info, to_output_data=False):
    resulted_event, remove_from_candidates, sim, token_sim, league_sim, is_swapped = await match_event(event, compared_source, parameters, info, to_output_data=to_output_data)

    if resulted_event is not None:

        existed_result = result.get(resulted_event['bk_event_id'], None)
        if result.get(resulted_event['bk_event_id'], None) is not None:
            if existed_result[1] < sim:
                old_event = get_event(test_source, existed_result[0])
                compared_source_copy = compared_source.copy()
                compared_source_copy.remove(resulted_event)
                if remove_from_candidates:
                    compared_source.remove(resulted_event)
                result[resulted_event['bk_event_id']] = (event['bk_event_id'], sim, token_sim, league_sim, is_swapped)
                result, _ = await recursed_match(result, old_event, test_source, compared_source_copy, parameters, info)
            else:
                compared_source_copy = compared_source.copy()
                compared_source_copy.remove(resulted_event)
                result, _ = await recursed_match(result, event, test_source, compared_source_copy, parameters, info)
        else:
            if remove_from_candidates:
                compared_source.remove(resulted_event)
            result[resulted_event['bk_event_id']] = (event['bk_event_id'], sim, token_sim, league_sim, is_swapped)

    return result, compared_source


async def recursed_custom_match(result, event, test_source, compared_source, parameters):
    resulted_event, remove_from_candidates, sim, token_sim, league_sim, is_swapped = await match_event(event, compared_source, parameters, custom=True)

    if resulted_event is not None:

        existed_result = result.get(resulted_event['event_id'], None)
        if result.get(resulted_event['event_id'], None) is not None:
            if existed_result[1] < sim:
                old_event = get_event_for_custom(test_source, existed_result[0])
                compared_source_copy = compared_source.copy()
                compared_source_copy.remove(resulted_event)
                if remove_from_candidates:
                    compared_source.remove(resulted_event)
                result[resulted_event['event_id']] = (event['event_id'], sim, token_sim, league_sim, is_swapped)
                result, _ = await recursed_custom_match(result, old_event, test_source, compared_source_copy, parameters)
            else:
                compared_source_copy = compared_source.copy()
                compared_source_copy.remove(resulted_event)
                result, _ = await recursed_custom_match(result, event, test_source, compared_source_copy, parameters)
        else:
            if remove_from_candidates:
                compared_source.remove(resulted_event)
            result[resulted_event['event_id']] = (event['event_id'], sim, token_sim, league_sim, is_swapped)

    return result, compared_source


def event_equality(event, matched_event):
    event_team1_prep = preprocess_string(event['team1'])
    event_team2_prep = preprocess_string(event['team2'])
    event_team1_translit = transliterate(event['team1'])
    event_team2_translit = transliterate(event['team2'])
    event_league_prep = transliterate(event['league_name'])
    event_league_translit = transliterate(event['league_name'])
    if event_league_prep == matched_event.get('league_prep') or \
       event_league_prep == matched_event.get('league_translit') or \
       event_league_translit == matched_event.get('league_prep') or \
       event_league_translit == matched_event.get('league_translit'):
        if event_team1_prep == matched_event.get('team1_prep') or \
           event_team1_prep == matched_event.get('team1_translit') or \
           event_team1_translit == matched_event.get('team1_prep') or \
           event_team1_translit == matched_event.get('team1_translit'):
            if event_team2_prep == matched_event.get('team2_prep') or \
               event_team2_prep == matched_event.get('team2_translit') or \
               event_team2_translit == matched_event.get('team2_prep') or \
               event_team2_translit == matched_event.get('team2_translit'):
                return True
            return False
        else:
            if event_team1_prep == matched_event.get('team2_prep') or \
               event_team1_prep == matched_event.get('team2_translit') or \
               event_team1_translit == matched_event.get('team2_prep') or \
               event_team1_translit == matched_event.get('team2_translit'):
                if event_team2_prep == matched_event.get('team1_prep') or \
                   event_team2_prep == matched_event.get('team1_translit') or \
                   event_team2_translit == matched_event.get('team1_prep') or \
                   event_team2_translit == matched_event.get('team1_translit'):
                    return True
                return False
    return False

def find_matched_clone(matched_event1, matched_event2, source):
    for event in source:
        if event_equality(event, matched_event1):
            return 1, event
        if matched_event2 is not None:
            if event_equality(event, matched_event2):
                return 2, event
    return None, None


def check_whitelist(whitelist, test_source, compared_source, result):
    for matched_events in whitelist:
        matched_event1 = {
                    'team1_prep': preprocess_string(matched_events.get('event1.team1')),
                    'team2_prep': preprocess_string(matched_events.get('event1.team1')),
                    'league_prep': preprocess_string(matched_events.get('event1.league')),
                    'team1_translit': transliterate(matched_events.get('event1.team1')),
                    'team2_translit': transliterate(matched_events.get('event1.team1')),
                    'league_translit': transliterate(matched_events.get('event1.league')),
                  }
        matched_event2 = {
                    'team1_prep': preprocess_string(matched_events.get('event2.team1')),
                    'team2_prep': preprocess_string(matched_events.get('event2.team1')),
                    'league_prep': preprocess_string(matched_events.get('event2.league')),
                    'team1_translit': transliterate(matched_events.get('event2.team1')),
                    'team2_translit': transliterate(matched_events.get('event2.team1')),
                    'league_translit': transliterate(matched_events.get('event2.league')),
        }
        is_swapped = bool(matched_events.get('is_swapped'))
        is_match, test_event = find_matched_clone(matched_event1, matched_event2, test_source)
        if is_match is None or test_event is None:
            continue
        if is_match == 1:
            is_match, compared_event = find_matched_clone(matched_event1, None, compared_source)
        else:
            is_match, compared_event = find_matched_clone(matched_event2, None, compared_source)

        if is_match is None or compared_event is None:
            continue
        result[compared_event['bk_event_id']] = (test_event['bk_event_id'], 100, 100, 100, is_swapped)
        test_source.remove(test_source)
        compared_source.remove(compared_source)
    return test_source, compared_source, result

def pair_in_banlist(banlist, event1, event2):
    for ban_events in banlist:
        ban_event1 = {
            'team1_prep': preprocess_string(ban_events.get('event1.team1')),
            'team2_prep': preprocess_string(ban_events.get('event1.team1')),
            'league_prep': preprocess_string(ban_events.get('event1.league')),
            'team1_translit': transliterate(ban_events.get('event1.team1')),
            'team2_translit': transliterate(ban_events.get('event1.team1')),
            'league_translit': transliterate(ban_events.get('event1.league')),
        }
        ban_event2 = {
            'team1_prep': preprocess_string(ban_events.get('event2.team1')),
            'team2_prep': preprocess_string(ban_events.get('event2.team1')),
            'league_prep': preprocess_string(ban_events.get('event2.league')),
            'team1_translit': transliterate(ban_events.get('event2.team1')),
            'team2_translit': transliterate(ban_events.get('event2.team1')),
            'league_translit': transliterate(ban_events.get('event2.league')),
        }
        if (event_equality(event1, ban_event1) and event_equality(event2, ban_event2)) or \
            (event_equality(event2, ban_event1) and event_equality(event1, ban_event2)):
            return True
    return False

def check_banlist(banlist, report):
    final_report = report.copy()
    for resulted_pair in report:
        resulted_event1 = resulted_pair.get('event1')
        resulted_event2 = resulted_pair.get('event2')
        if pair_in_banlist(banlist, resulted_event1, resulted_event2):
            final_report.remove(resulted_pair)
    return report


async def match(events1: List,
                events2: List,
                parameters: Dict[str, float],
                info: Dict,
                whitelist: List[Dict],
                banlist: List[Dict],
                to_output_data: bool = False):

    if len(events1) > len(events2):
        compared_source = events1
        test_source = events2
    else:
        compared_source = events2
        test_source = events1
    result = {}
    test_source_copy = test_source.copy()
    compared_source_copy = compared_source.copy()
    test_source, compared_source, result = check_whitelist(whitelist, test_source, compared_source, result)
    for event in test_source:
        result, compared_source = await recursed_match(result, event, test_source, compared_source, parameters, info, to_output_data=to_output_data)
    pairs = get_report(result, test_source_copy, compared_source_copy)
    final_pairs = check_banlist(banlist, pairs)
    return final_pairs


async def check_events(events1: List, events2: List, parameters: Dict[str, float], sport_name: str, is_cyber: str):
    if len(events1) > len(events2):
        compared_source = events1
        test_source = events2
    else:
        compared_source = events2
        test_source = events1
    result = {}
    test_source_copy = test_source.copy()
    compared_source_copy = compared_source.copy()
    for event in test_source:
        result, compared_source = await recursed_custom_match(result, event, test_source, compared_source, parameters)
    pairs = get_custom_report(result, test_source_copy, compared_source_copy, sport_name, is_cyber)
    return pairs


# async def check_events(event1: Dict, event2: Dict, parameters: Dict[str, float]):
#     """
#     :param event1:
#     :param event2:
#     :param parameters:
#     :return: final_sim, token_sim, league_sim, is_match
#     """
#     min_sim = parameters.get('MINIMAL_SIM_THRESHOLD')
#
#     base_token_sim, base_league_sim, base_is_swapped = compute_check_similarity(preprocess_string, event1, event2)
#     translit_token_sim, translit_league_sim, translit_is_swapped = compute_check_similarity(transliterate, event1, event2)
#     token_sim = max(base_token_sim, translit_token_sim)
#     league_sim = max(base_league_sim, translit_league_sim)
#     is_swapped = base_is_swapped or translit_is_swapped
#
#     final_sim = token_sim * parameters.get('FINAL_SIM_RATIO') + league_sim * (1 - parameters.get('FINAL_SIM_RATIO'))
#
#     is_match = False
#     if final_sim > min_sim:
#         is_match = True
#
#     return final_sim, token_sim, league_sim, is_match, is_swapped


def compute_check_similarity(transformation, event1, event2):
    event1_token1 = transformation(event1['team1'])
    event1_token2 = transformation(event1['team2'])
    event2_token1 = transformation(event2['team1'])
    event2_token2 = transformation(event2['team2'])

    event1_league = transformation(event1['league'])
    event2_league = transformation(event2['league'])

    plain_token_similarities = [mean([get_similarity(event1_token1, event2_token1),
                                      get_similarity(event1_token2, event2_token2)])
                                ]
    swapped_token_similarities = [mean([get_similarity(event1_token1, event2_token2),
                                        get_similarity(event1_token2, event2_token1)])
                                  ]
    league_similarities = [get_similarity(event1_league, event2_league)]

    if transformation != preprocess_string:
        # cross-transforms variations
        base_event1_token1 = preprocess_string(event1['team1'])
        base_event1_token2 = preprocess_string(event1['team2'])
        base_event2_token1 = preprocess_string(event2['team1'])
        base_event2_token2 = preprocess_string(event2['team2'])

        base_event1_league = preprocess_string(event1['league'])
        base_event2_league = preprocess_string(event2['league'])

        plain_token_similarities += [
            mean([get_similarity(event1_token1, base_event2_token1),
                  get_similarity(event1_token2, base_event2_token2)]),
            mean([get_similarity(base_event1_token1, event2_token1),
                  get_similarity(base_event1_token2, event2_token2)]),
        ]

        swapped_token_similarities += [
            mean([get_similarity(event1_token1, base_event2_token2),
                  get_similarity(event1_token2, base_event2_token1)]),
            mean([get_similarity(base_event1_token1, event2_token2),
                  get_similarity(base_event1_token2, event2_token1)]),
        ]
        league_similarities += [
            get_similarity(event1_league, base_event2_league),
            get_similarity(base_event1_league, event2_league)
        ]
    max_plain_token_similarity = max(plain_token_similarities)
    max_swapped_token_similarity = max(swapped_token_similarities)
    is_swapped = max_swapped_token_similarity > max_plain_token_similarity

    return max([max_swapped_token_similarity, max_plain_token_similarity]), max(league_similarities), is_swapped



def get_parameters_match(data):
    """

    """
    result = []
    token_sim_true_list = []
    league_sim_true_list = []
    for pair in data:
        base_token_sim, base_league_sim, _ = compute_similarity(preprocess_string, pair['event1'], pair['event2'])
        translit_token_sim, translit_league_sim, _ = compute_similarity(transliterate, pair['event1'], pair['event2'])
        token_sim_true = max(base_token_sim, translit_token_sim)
        league_sim_true = max(base_league_sim, translit_league_sim)
        token_sim_true_list.append(token_sim_true)
        league_sim_true_list.append(league_sim_true)
    flag_token_sim_list = False
    if len(data) > 1:
        token_sim_false_list = []
        league_sim_false_list = []
        flag_token_sim_list = True
        for x, event1 in enumerate(data):
            for y, event2 in enumerate(data):
                if x == y:
                    continue
                base_token_sim, base_league_sim, _ = compute_similarity(preprocess_string, event1['event1'], event2['event2'])
                translit_token_sim, translit_league_sim, _ = compute_similarity(transliterate, event1['event1'], event2['event2'])
                token_sim_false = max(base_token_sim, translit_token_sim)
                league_sim_false = max(base_league_sim, translit_league_sim)
                token_sim_false_list.append(token_sim_false)
                league_sim_false_list.append(league_sim_false)

    # Определение final_sim_ratio по token_sim и league_sim пар и ложных событий
    average_token_sim_true = mean(token_sim_true_list)
    average_league_sim_true = mean(league_sim_true_list)

    if flag_token_sim_list:
        final_sim_ratio_arg = []
        final_sim_ratio_arg.append(average_token_sim_true / 100)
        final_sim_ratio_arg.append(average_token_sim_true ** 2 / (average_token_sim_true ** 2 + average_league_sim_true ** 2))
        average_token_sim_false = mean(token_sim_false_list)
        average_league_sim_false = mean(league_sim_false_list)
        dif_average_token_sim = average_token_sim_true - average_token_sim_false
        dif_average_league_sim = average_league_sim_true - average_league_sim_false
        if dif_average_token_sim <= 0:
            final_sim_ratio_arg.append(0)
        if dif_average_league_sim <= 0:
            final_sim_ratio_arg.append(1)
        if dif_average_token_sim >= 0 and dif_average_league_sim >= 0:
            final_sim_ratio_arg.append(dif_average_token_sim**2/(dif_average_token_sim**2 + dif_average_league_sim**2))
        min_token_sim_true = min(token_sim_true_list)
        min_league_sim_true = min(league_sim_true_list)
        max_token_sim_false = max(token_sim_false_list)
        max_league_sim_false = max(league_sim_false_list)
        if min_token_sim_true > max_token_sim_false:
            final_sim_ratio_arg.append(1)
        if min_league_sim_true > max_league_sim_false:
            final_sim_ratio_arg.append(0)
    final_sim_ratio = mean(final_sim_ratio_arg)

    similarity_coefficient_list_true = []
    for i, token_sim_true in enumerate(token_sim_true_list):
        similarity_coefficient_true = token_sim_true * final_sim_ratio + league_sim_true_list[i] * (1 - final_sim_ratio)
        similarity_coefficient_list_true.append(similarity_coefficient_true)
    if flag_token_sim_list:
        similarity_coefficient_list_false = []
        for i, token_sim_false in enumerate(token_sim_false_list):
            similarity_coefficient_false = token_sim_false * final_sim_ratio + league_sim_false_list[i] * (1 - final_sim_ratio)
            similarity_coefficient_list_false.append(similarity_coefficient_false)

        if min(similarity_coefficient_list_true) > max(similarity_coefficient_list_false):
            minimal_sim_threshold = mean([min(similarity_coefficient_list_true),
                                          max(similarity_coefficient_list_false)])
        else:
            minimal_sim_threshold = min(similarity_coefficient_list_true) * 0.9

        if mean(similarity_coefficient_list_true) > max(similarity_coefficient_list_false):
            remove_candidate_threshold = mean([mean(similarity_coefficient_list_true),
                                               max(similarity_coefficient_list_false)])
        else:
            remove_candidate_threshold = mean([max(similarity_coefficient_list_true),
                                               max(similarity_coefficient_list_false)])

        # if mean(similarity_coefficient_list_true) > max(similarity_coefficient_list_false):
        #     confident_threshold = mean([max(similarity_coefficient_list_true),
        #                                 mean(similarity_coefficient_list_true)])
        # else:
        #     confident_threshold = max(similarity_coefficient_list_true) * 0.9
    else:
        minimal_sim_threshold = min(similarity_coefficient_list_true) * 0.9
        remove_candidate_threshold = mean(similarity_coefficient_list_true)
        confident_threshold = mean([max(similarity_coefficient_list_true), mean(similarity_coefficient_list_true)])
    result = {
        "final_sim_ratio": final_sim_ratio,
        "minimal_sim_threshold": minimal_sim_threshold,
        "remove_candidate_threshold": remove_candidate_threshold,
        "confident_threshold": confident_threshold
    }
    return result