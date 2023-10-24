import datetime

import simplejson as json
from src.service_layer.utils import handle_error, make_response
from src.config import TEST_MATCHER
from src.uof import PostgresUnitOfWork
import src.exceptions as exceptions
import asyncio
from asyncio.exceptions import TimeoutError
import aiohttp
import logging
import json
import hashlib
import copy
import random
from collections import defaultdict

logger = logging.getLogger("backend-matcher")


# async def get_custom_match_results(uof: PostgresUnitOfWork, unmatched: bool = True):
#     async with uof:
#         try:
#             await uof.begin()
#             results = await uof.custom_match_repo.get_custom_results(unmatched)
#             results = [
#                 {
#                     'event1': json.loads(event1),
#                     'event2': json.loads(event2),
#                     'overall_similarity': overall_similarity,
#                     'teams_similarity': teams_similarity,
#                     'league_similarity': league_similarity,
#                     'sport': sport,
#                     'is_cyber': is_cyber,
#                     'is_swapped': is_swapped,
#                     'is_match': is_match,
#
#                 }
#                 for id,
#                     event1,
#                     event2,
#                     overall_similarity,
#                     teams_similarity,
#                     league_similarity,
#                     sport,
#                     is_cyber,
#                     is_swapped,
#                     is_match
#                 in results
#             ]
#             await uof.commit()
#
#             if unmatched:
#                 logger.info(f'Get all unmatched results - OK')
#             else:
#                 logger.info(f'Get all results - OK')
#             return make_response(result=results)
#         except Exception as e:
#             return await handle_error(uof, e)
#
#
# async def run_custom_match(uof: PostgresUnitOfWork, data, all_results=False):
#     """
#     :param uof:
#     :param request Optional
#     {
#          {
#             sport: str,
#             event1: {
#                 team1: str,
#                 team2: str,
#                 league: str
#             },
#             event2: {
#                 team1: str,
#                 team2: str,
#                 league: str
#             },
#             is_cyber: bool
#         }
#     }
#     """
#     async with uof:
#         try:
#             await uof.begin()
#
#             # Берем json из файла, если он не пришел запросом
#             if not data:
#                 with open('temp.json', 'r') as file:
#                     data = json.load(file)
#
#
#
#             async with aiohttp.ClientSession() as session:
#                 logger.info(f"Data for quality check has been sent to test_ matcher")
#                 async with session.post(TEST_MATCHER + '/check_quality/', json=data) as resp:
#                     if resp.ok:
#                         logger.info(f"Result data from test_ matcher successfully received")
#                         response_data = await resp.json()
#                         check_results = response_data.get('check_result')
#
#                         processed_count = len(check_results)
#                         positive_processed = sum([1 for result in check_results if result.get('is_match', False)])
#                         negative_processed = processed_count - positive_processed
#
#                         for result in check_results:
#                             _ = await uof.custom_match_repo.save_all_data(**result)
#                         await uof.commit()
#
#                         negative_results = [result for result in check_results if not result.get('is_match', False)]
#
#                         for result in negative_results:
#                             _ = await uof.custom_match_repo.save_unmatched_data(**result)
#                         await uof.commit()
#
#                         response = {
#                             "statistics": {
#                                 "processed_count": processed_count,
#                                 "positive_matched": positive_processed,
#                                 "negative_matched": negative_processed
#                             },
#                             "unmatched_results": negative_results,
#                         }
#
#                         if all_results:
#                             response["all_results"] = check_results
#
#                         logger.info(f"Result data from test_ matcher successfully processed")
#                         return make_response(result=response)
#                     else:
#                         logger.error(f'Request to test_ matcher failed! {resp.reason}')
#                         return make_response(status_code=500, detail=f'Request to test_ matcher failed! {resp.reason}')
#
#         except Exception as e:
#             await uof.rollback()
#             logger.error(f"Something went wrong:\n{e}")
#             return make_response(status_code=500, detail=f"Something went wrong:\n{e}")


async def run_custom_match_stable(uof: PostgresUnitOfWork, input_data, date):
    """
    :param uof:
    :param request Optional
    [
        {
            date: str,
            data: [
                {
                    "sport": str,
                    "event1": {
                                "event_id": str(uuid4),
                                "event_name": str,
                                "league": str,
                                "team1": str,
                                "team2": str
                                },
                    "event2": {
                                "event_id": str(uuid4),
                                "event_name": str,
                                "league": str,
                                "team1": str,
                                "team2": str
                                },
                    "is_cyber": int
                },
                { sport: str, event1: Dict, even2: Dict, is_cyber: int}
            ]
        },
        { date: str, data: Dict},
        {...}
    ]
    """
    async with uof:
        try:
            await uof.begin()

            sha256_hash = ''

            # Берем json из файла, если он не пришел запросом
            if not input_data:
                with open('input_data.json', 'r') as file:
                    input_data = json.load(file)
                for input_dict in input_data:
                    if date and input_dict['date'] == date:
                        sha256_hash = calculate_hash(input_dict['data'])
                if not sha256_hash:
                    sha256_hash = calculate_hash(input_data)
            else:
                sha256_hash = calculate_hash(input_data)

            results = await uof.custom_match_repo.get_processed_data_info()
            results = [
                {
                    'hash': hash,
                    'total_pairs_sent': total_pairs_sent,
                    'correct_matches': correct_matches,
                    'mismatched_pairs': mismatched_pairs,
                    'unmatched_results': unmatched_results,
                    'correct_matches_percentage': correct_matches_percentage,
                    'mismatched_pairs_percentage': mismatched_pairs_percentage,
                    'unmatched_pairs_percentage': unmatched_pairs_percentage,
                    'process_start': process_start,
                    'process_end': process_end
                }
                for hash,
                    total_pairs_sent,
                    correct_matches,
                    mismatched_pairs,
                    unmatched_results,
                    correct_matches_percentage,
                    mismatched_pairs_percentage,
                    unmatched_pairs_percentage,
                    id,
                    process_start,
                    process_end
                in results
            ]
            await uof.commit()

            process_start = datetime.datetime.now()

            for result in results:
                if result['hash'] == sha256_hash:
                    logger.info('For this dataset, the matcher has already been launched')
                    return make_response(
                        result={"reason": "For this dataset, the matcher has already been launched",
                                "data": result}
                    )

            response = {
                "stats": {},
                "matched_pairs": [],
                "mismatched_pairs": [],
                "unmatched_results_id": [],
                "unmatched_results": {
                    "bk1": {
                        "data": [],
                    },
                    "bk2": {
                        "data": [],
                    }
                },
            }

            stats = {
                "total_pairs_sent": 0,
                "correct_matches": 0,
                "mismatches": 0,
                "unmatched": 0,
                "by_dates": {},
            }

            for input_dict in input_data:
                if date and input_dict["date"] != date:
                    continue

                processed_date = input_dict["date"]

                output_data = {
                    "bk1": {
                        "data": []
                    },
                    "bk2": {
                        "data": []
                    }
                }

                original_pairs_ids = set()
                logger.info(f'Input data:\n{input_dict}')

                for item in input_dict['data']:
                    for i in [1, 2]:
                        output_data[f"bk{i}"]["data"].append({
                            "event_id": item[f"event{i}"]["event_id"],
                            "sport": item["sport"],
                            "event_name": item[f"event{i}"]["event_name"],
                            "team1": item[f"event{i}"]["team1"],
                            "team2": item[f"event{i}"]["team2"],
                            "league_name": item[f"event{i}"]["league"],
                            "is_cyber": bool(item["is_cyber"]),
                        })
                    original_pairs_ids.add((item["event1"]["event_id"], item["event2"]["event_id"]))

                stats["total_pairs_sent"] += len(original_pairs_ids)
                stats["by_dates"][processed_date] = {}
                stats["by_dates"][processed_date]["pairs_sent"] = len(original_pairs_ids)

                logger.info(f'Output data for {processed_date} date:\n{output_data}')

                random.shuffle(output_data["bk2"]["data"])
                try:
                    timeout = aiohttp.ClientTimeout(total=3600)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        logger.info(f"Data for quality check for {input_dict['date']} has been sent to test matcher")
                        async with session.post(TEST_MATCHER + '/check_quality/', json=output_data) as resp:
                            if resp.ok:
                                logger.info(f"Result data from test matcher successfully received")
                                response_data = await resp.json()
                                check_results = response_data.get('check_result')

                                matched_pairs_ids = set((pair["event1"]["event_id"], pair["event2"]["event_id"]) for pair in check_results['matched_pairs'])
                                matched_pairs = check_results['matched_pairs']
                                unmatched_results_ids = check_results['unmatched_events']
                                unmatched_results = copy.deepcopy(output_data)

                                unmatched_results['bk1']['data'] = [item for item in unmatched_results['bk1']['data'] if
                                                                    item['event_id'] in unmatched_results_ids]
                                unmatched_results['bk2']['data'] = [item for item in unmatched_results['bk2']['data'] if
                                                                    item['event_id'] in unmatched_results_ids]

                                mismatches = []

                                correct_matches_ids = [(pair[0], pair[1]) for pair in matched_pairs_ids if pair in original_pairs_ids]
                                for pair in matched_pairs_ids:
                                    if pair not in original_pairs_ids:
                                        for matched_pair in matched_pairs:
                                            if matched_pair['event1']['event_id'] == pair[0] and matched_pair['event2']['event_id'] == pair[1]:
                                                matched_pair['mismatch'] = True
                                                mismatches.append(matched_pair)

                                response["matched_pairs"].extend(matched_pairs)
                                response["mismatched_pairs"].extend(mismatches)
                                response["unmatched_results_id"].extend(unmatched_results_ids)
                                response["unmatched_results"]['bk1']['data'].extend(unmatched_results['bk1']['data'])
                                response["unmatched_results"]['bk2']['data'].extend(unmatched_results['bk2']['data'])

                                stats["correct_matches"] += len(correct_matches_ids) - len(mismatches)
                                stats["mismatches"] += len(mismatches)
                                stats["unmatched"] += len(unmatched_results_ids)
                                stats["by_dates"][processed_date]["correct_matches"] = len(correct_matches_ids) - len(mismatches)
                                stats["by_dates"][processed_date]["mismatches"] = len(mismatches)
                                stats["by_dates"][processed_date]["unmatched"] = len(unmatched_results_ids)

                                for result in matched_pairs:
                                    _ = await uof.custom_match_repo.save_all_data(processed_date, **result)
                                await uof.commit()

                                for result in unmatched_results['bk1']['data']:
                                    _ = await uof.custom_match_repo.save_unmatched_data(processed_date, **result)
                                await uof.commit()
                                for result in unmatched_results['bk2']['data']:
                                    _ = await uof.custom_match_repo.save_unmatched_data(processed_date, **result)
                                await uof.commit()

                                logger.info(f"Result data for {input_dict['date']} from test matcher successfully processed")
                            else:
                                logger.error(f'Request to test matcher failed! {resp.reason}')
                                return make_response(status_code=500, detail=f'Request to test matcher failed! {resp.reason}')
                except TimeoutError:
                    logger.warning(f"Timeout error for quality check for {input_dict['date']}")

            process_end = datetime.datetime.now()
            _ = await uof.custom_match_repo.save_processed_data_info(sha256_hash, process_start, process_end, **stats)
            await uof.commit()

            logger.info(stats)
            response["stats"] = stats
            return make_response(result=response)

        except Exception as e:
            await uof.rollback()
            logger.exception(f"Something went wrong:\n{e}")
            return make_response(status_code=500, detail=f"Something went wrong: {e}")


async def get_custom_match_results_stable(uof: PostgresUnitOfWork, date: str):
    async with uof:
        await data_dump(uof, date)
        logger.info(f'Save all results to file - OK')
        return make_response(result='Data successfully saved at processed_data.json')


async def data_dump(uof: PostgresUnitOfWork, date: str, without_crossed: bool):
    try:
        matched_pairs = await uof.custom_match_repo.get_matched_results(date)
        matched_pairs = [
            {
                'event1': json.loads(event1),
                'event2': json.loads(event2),
                'overall_similarity': overall_similarity,
                'teams_similarity': teams_similarity,
                'league_similarity': league_similarity,
                'sport': sport,
                'is_cyber': is_cyber,
                'is_swapped': is_swapped,
                'is_match': is_match,
                'mismatch': mismatch,
                'event1_id': str(event1_id),
                'event2_id': str(event2_id),
                'date': date
            }
            for id,
                event1,
                event2,
                overall_similarity,
                teams_similarity,
                league_similarity,
                sport,
                is_cyber,
                is_swapped,
                is_match,
                event1_id,
                event2_id,
                date,
                mismatch
            in matched_pairs
        ]

        matched_count = len(matched_pairs)
        mismatched_pairs = [pair for pair in matched_pairs if pair['mismatch']]
        mismatch_count = len(mismatched_pairs)
        correct_matches = matched_count - mismatch_count
        results = {
            "stats": {
              "total_pairs_sent": 0,
              "correct_matches": correct_matches,
              "mismatched_pairs": mismatch_count,
              "unmatched_results": 0,
              "correct_matches_percentage": '',
              "mismatched_pairs_percentage": '',
            },
            "matched_pairs": matched_pairs,
            "mismatched_pairs": mismatched_pairs,
        }

        stats_by_date = defaultdict(lambda: {"pairs_sent": 0,
                                             "correct_matches": 0,
                                             "mismatched_pairs": 0,
                                             "unmatched_results": 0,
                                             "correct_matches_percentage": '',
                                             "mismatched_pairs_percentage": '',
                                             "unmatched_pairs_percentage": ''})

        for matched_pair in matched_pairs:
            date_db = matched_pair['date']
            stats_by_date[date_db]['pairs_sent'] += 1
            if not matched_pair['mismatch']:
                stats_by_date[date_db]['correct_matches'] += 1
                stats_by_date[date_db]['correct_matches_percentage'] = f"{round(stats_by_date[date_db]['correct_matches'] / stats_by_date[date_db]['pairs_sent'] * 100, 2)}%"
            else:
                stats_by_date[date_db]['mismatched_pairs'] += 1
                stats_by_date[date_db]['mismatched_pairs_percentage'] = f"{round(stats_by_date[date_db]['mismatched_pairs'] / stats_by_date[date_db]['pairs_sent'] * 100, 2)}%"

        unmatched_results = await uof.custom_match_repo.get_unmatched_results(date)
        unmatched_results = [
            {
                'event_id': str(event_id),
                'date': date_db,
                'event_name': event_name,
                'team1': team1,
                'team2': team2,
                'league_name': league_name,
                'sport': sport,
                'is_cyber': is_cyber,
            }
            for event_id,
                date_db,
                event_name,
                team1,
                team2,
                league_name,
                sport,
                is_cyber
            in unmatched_results
        ]

        for unmatched_result in unmatched_results:
            date_db = unmatched_result['date']
            stats_by_date[date_db]['pairs_sent'] += 0.5
            stats_by_date[date_db]['unmatched_results'] += 1
            if stats_by_date[date_db]['pairs_sent'] % 1 == 0:
                stats_by_date[date_db]['pairs_sent'] = int(stats_by_date[date_db]['pairs_sent'])
                stats_by_date[date_db]['unmatched_pairs_percentage'] = f"{round(stats_by_date[date_db]['unmatched_results'] / 2 / stats_by_date[date_db]['pairs_sent'] * 100, 2)}%"
                stats_by_date[date_db]['correct_matches_percentage'] = f"{round(stats_by_date[date_db]['correct_matches'] / stats_by_date[date_db]['pairs_sent'] * 100, 2)}%"
                stats_by_date[date_db]['mismatched_pairs_percentage'] = f"{round(stats_by_date[date_db]['mismatched_pairs'] / stats_by_date[date_db]['pairs_sent'] * 100, 2)}%"

        results['unmatched_results'] = unmatched_results
        unmatched_count = len(unmatched_results)
        results['stats']['unmatched_results'] = unmatched_count

        total_pairs_sent = int(matched_count + unmatched_count/2)
        results['stats']['total_pairs_sent'] = total_pairs_sent

        correct_matches_percentage = round(correct_matches / total_pairs_sent * 100, 2)
        results['stats']['correct_matches_percentage'] = f"{correct_matches_percentage}%"

        mismatched_pairs_percentage = round(mismatch_count / total_pairs_sent * 100, 2)
        results['stats']['mismatched_pairs_percentage'] = f"{mismatched_pairs_percentage}%"

        unmatched_pairs_percentage = round(unmatched_count / 2 / total_pairs_sent * 100, 2)
        results['stats']['unmatched_pairs_percentage'] = f"{unmatched_pairs_percentage}%"

        results['stats']['by_dates'] = dict(stats_by_date)

        out_file = 'processed_data.json' if not without_crossed else 'processed_data_afterClean.json'

        with open(f'/custom_match/{out_file}', 'w') as outfile:
            json.dump(results, outfile, indent=2)

    except Exception as e:
        logger.exception(e)
        return await handle_error(uof, e)


async def run_custom_match(uof: PostgresUnitOfWork, filename, input_data, date, pool, without_crossed):
    """
    :param uof:
    :param request Optional
    [
        {
            date: str,
            data: [
                {
                    "sport": str,
                    "event1": {
                                "event_id": str(uuid4),
                                "event_name": str,
                                "league": str,
                                "team1": str,
                                "team2": str
                                },
                    "event2": {
                                "event_id": str(uuid4),
                                "event_name": str,
                                "league": str,
                                "team1": str,
                                "team2": str
                                },
                    "is_cyber": int
                },
                { sport: str, event1: Dict, even2: Dict, is_cyber: int}
            ]
        },
        { date: str, data: Dict},
        {...}
    ]
    """
    async with uof:
        try:
            await uof.begin()

            sha256_hash = ''

            # Берем json из файла, если он не пришел запросом
            if not input_data:
                with open(f'/custom_match/{filename}', 'r') as file:
                    input_data = json.load(file)
                for input_dict in input_data:
                    if date and input_dict['date'] == date:
                        sha256_hash = calculate_hash(input_dict['data'])
                if not sha256_hash:
                    sha256_hash = calculate_hash(input_data)
            else:
                sha256_hash = calculate_hash(input_data)

            results = await uof.custom_match_repo.get_processed_data_info()
            results = [
                {
                    'hash': hash,
                    'total_pairs_sent': total_pairs_sent,
                    'correct_matches': correct_matches,
                    'mismatched_pairs': mismatched_pairs,
                    'unmatched_results': unmatched_results,
                    'correct_matches_percentage': correct_matches_percentage,
                    'mismatched_pairs_percentage': mismatched_pairs_percentage,
                    'unmatched_pairs_percentage': unmatched_pairs_percentage,
                    'process_start': process_start,
                    'process_end': process_end
                }
                for hash,
                    total_pairs_sent,
                    correct_matches,
                    mismatched_pairs,
                    unmatched_results,
                    correct_matches_percentage,
                    mismatched_pairs_percentage,
                    unmatched_pairs_percentage,
                    id,
                    process_start,
                    process_end
                in results
            ]

            for result in results:
                if result['hash'] == sha256_hash:
                    logger.info('For this dataset, the matcher has already been launched')
                    return make_response(
                        result={"reason": "For this dataset, the matcher has already been launched",
                                "data": result}
                    )

            process_start = datetime.datetime.now()

            _ = await uof.custom_match_repo.save_custom_match_start_info(sha256_hash, process_start)
            await uof.commit()

            additional_uof = PostgresUnitOfWork(pool)
            asyncio.ensure_future(run_custom_match_background(additional_uof, filename, input_data, date, sha256_hash, without_crossed))

            result = {
                "reason": "Matcher started in the background",
                'hash': sha256_hash,
                'start_date': process_start,
            }

            return make_response(result=result)

        except Exception as e:
            await uof.rollback()
            logger.exception(f"Something went wrong:\n{e}")
            return make_response(status_code=500, detail=f"Something went wrong: {e}")


async def run_custom_match_background(uof: PostgresUnitOfWork, filename, input_data, date, sha256_hash, without_crossed):
    async with uof:
        try:
            await uof.begin()
            stats = {
                "total_pairs_sent": 0,
                "correct_matches": 0,
                "mismatches": 0,
                "unmatched": 0,
            }

            for input_dict in input_data:
                if date and input_dict["date"] != date:
                    continue

                processed_date = input_dict["date"]

                output_data = {
                    "bk1": {
                        "data": []
                    },
                    "bk2": {
                        "data": []
                    }
                }

                original_pairs_ids = set()
                logger.info(f'Input data:\n{input_dict}')

                for item in input_dict['data']:
                    for i in [1, 2]:
                        output_data[f"bk{i}"]["data"].append({
                            "event_id": item[f"event{i}"]["event_id"],
                            "sport": item["sport"],
                            "event_name": item[f"event{i}"]["event_name"],
                            "team1": item[f"event{i}"]["team1"],
                            "team2": item[f"event{i}"]["team2"],
                            "league_name": item[f"event{i}"]["league"],
                            "is_cyber": bool(item["is_cyber"]),
                        })
                    original_pairs_ids.add((item["event1"]["event_id"], item["event2"]["event_id"]))

                stats["total_pairs_sent"] += len(original_pairs_ids)

                logger.info(f'Output data for {processed_date} date:\n{output_data}')

                random.shuffle(output_data["bk2"]["data"])
                try:
                    timeout = aiohttp.ClientTimeout(total=3600)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        logger.info(f"Data for quality check for {input_dict['date']} has been sent to test matcher")
                        async with session.post(TEST_MATCHER + '/check_quality/', json=output_data) as resp:
                            if resp.ok:
                                logger.info(f"Result data from test matcher successfully received")
                                response_data = await resp.json()
                                check_results = response_data.get('check_result')

                                matched_pairs_ids = set((pair["event1"]["event_id"], pair["event2"]["event_id"]) for pair in
                                                        check_results['matched_pairs'])
                                matched_pairs = check_results['matched_pairs']
                                unmatched_results_ids = check_results['unmatched_events']
                                unmatched_results = copy.deepcopy(output_data)

                                unmatched_results['bk1']['data'] = [item for item in unmatched_results['bk1']['data'] if
                                                                    item['event_id'] in unmatched_results_ids]
                                unmatched_results['bk2']['data'] = [item for item in unmatched_results['bk2']['data'] if
                                                                    item['event_id'] in unmatched_results_ids]

                                mismatches = []

                                correct_matches_ids = [(pair[0], pair[1]) for pair in matched_pairs_ids if
                                                       pair in original_pairs_ids]
                                for pair in matched_pairs_ids:
                                    if pair not in original_pairs_ids:
                                        for matched_pair in matched_pairs:
                                            if matched_pair['event1']['event_id'] == pair[0] and matched_pair['event2']['event_id'] == pair[1]:
                                                matched_pair['mismatch'] = True
                                                mismatches.append(matched_pair)

                                stats["correct_matches"] += len(correct_matches_ids) - len(mismatches)
                                stats["mismatches"] += len(mismatches)
                                stats["unmatched"] += len(unmatched_results_ids)

                                for result in matched_pairs:
                                    _ = await uof.custom_match_repo.save_all_data(processed_date, **result)
                                await uof.commit()

                                for result in unmatched_results['bk1']['data']:
                                    _ = await uof.custom_match_repo.save_unmatched_data(processed_date, **result)
                                await uof.commit()
                                for result in unmatched_results['bk2']['data']:
                                    _ = await uof.custom_match_repo.save_unmatched_data(processed_date, **result)
                                await uof.commit()

                                logger.info(f"Result data for {input_dict['date']} from test matcher successfully processed")
                            else:
                                logger.error(f'Request to test matcher failed! {resp.reason}')
                                return make_response(status_code=500, detail=f'Request to test matcher failed! {resp.reason}')
                except TimeoutError:
                    logger.warning(f"Timeout error for quality check for {input_dict['date']}")

            process_end = datetime.datetime.now()
            _ = await uof.custom_match_repo.save_custom_match_end_info(sha256_hash, process_end, **stats)
            await uof.commit()

            await data_dump(uof, date, without_crossed)
            logger.info(f'Save all results to file - OK')

            _ = await uof.custom_match_repo.truncate_tables()
            await uof.commit()

            logger.info(f'Tables "custom_matched_data" and "custom_unmatched_data" successfully truncated - OK')

        except Exception as e:
            await uof.rollback()
            logger.exception(f"Something went wrong:\n{e}")
            return make_response(status_code=500, detail=f"Something went wrong: {e}")


async def run_remove_crosshairs(uof: PostgresUnitOfWork):
    """
    :param uof:
    :param request Optional
    ...
    """
    async with uof:
        try:
            await uof.begin()

            # Берем json из файлы
            logger.info('start remove crosshairs')
            with open('/custom_match/processed_data.json', 'r') as file1:
                with open('/custom_match/input_data.json', 'r') as file2:
            # with open('processed_data.json', 'r') as file1:
            #     with open('input_data.json', 'r') as file2:
                    file1 = json.load(file1)
                    file2 = json.load(file2)
                    file2_for_del = copy.deepcopy(file2)
                    result_for_del = set()
                    resultElementList = {"resultElementList": []}
                    count = 0
                    for mismatch_pair in file1["mismatched_pairs"]:
                        event_id1_1x = mismatch_pair["event1"]["event_id"]
                        event_id1_2x = mismatch_pair["event2"]["event_id"]
                        sport = mismatch_pair["sport"]
                        date_event = mismatch_pair["date"]
                        for key_file2, date_events in enumerate(file2):
                            if date_event != date_events["date"]:
                                continue
                            data_array = date_events["data"]
                            for key, event_search in enumerate(data_array):
                                if event_id1_2x == event_search["event2"]["event_id"]:
                                    event_id1v = event_search["event1"]["event_id"]
                                    event_id2v = event_search["event2"]["event_id"]
                                    for mismatch_pair in file1["mismatched_pairs"]:
                                        event_id2_1x = mismatch_pair["event1"]["event_id"]
                                        event_id2_2x = mismatch_pair["event2"]["event_id"]
                                        if event_id1v == event_id2_1x:
                                            if not (event_id1_1x in result_for_del):
                                                resultElementList["resultElementList"].append(mismatch_pair)
                                            result_for_del.add(event_id2_1x)
                                            result_for_del.add(event_id1_1x)
                                            del_num = []
                                            for num_for_del, pair_for_del in enumerate(file2_for_del[key_file2]["data"]):
                                                if pair_for_del["event1"]["event_id"] == event_id2_1x:
                                                    del_num.append(num_for_del)
                                                if pair_for_del["event1"]["event_id"] == event_id1_1x:
                                                    del_num.append(num_for_del)
                                                if len(del_num) == 2:
                                                    count += 2
                                                    del file2_for_del[key_file2]["data"][del_num[1]]
                                                    del file2_for_del[key_file2]["data"][del_num[0]]
                                                    break
            result_for_del = list(result_for_del)
            save_name1 = "/custom_match/resultForDel.json"
            save_name2 = "/custom_match/input_data_without_crossed.json"
            # save_name1 = "resultForDel.json"
            # save_name2 = "input_data_without_crossed.json"
            with open(save_name1, 'w') as fp:
                json.dump(resultElementList, fp)
            with open(save_name2, 'w') as fp:
                json.dump(file2_for_del, fp)
            logger.info(f'Finish remove crosshairs. File saves to {save_name1} and {save_name1}')
            result = {
                'info': {
                    "count_del": count,
                    'path_to_file1': save_name1,
                    'path_to_file2': save_name2,
                },
                'result_for_del': result_for_del
            }
            return make_response(result=result)
        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            return make_response(status_code=500, detail=f"Something went wrong:\n{e}")


async def get_custom_match_status(uof: PostgresUnitOfWork, hash):

    try:
        async with uof:
            logger.info(f'start get_custom_match_status on {hash}')
            event = await uof.custom_match_repo.get_processed_data_info_by_id(hash)
            event = event[0]
            if not event[10]:
                result = f"matcher launched in {event[9]}"
            else:
                result = {
                    'total_pairs_sent': event[1],
                    'correct_matches': event[2],
                    'mismatched_pairs': event[3],
                    'unmatched_results': event[4],
                    'correct_matches_percentage': event[5],
                    'mismatched_pairs_percentage': event[6],
                    'unmatched_pairs_percentage': event[7],
                    'id': event[8],
                    'process_start': event[9],
                    'process_end': event[10],
                    'operation_time': event[10] - event[9],
                }
            logger.info(f'finish get_custom_match_status on {hash}, return {result}')
            return make_response(result=result)
    except exceptions.EntryDoesNotExist:
        logger.error(f"No entry with hash:{hash} in the database processed_data_info")
        return make_response(status_code=404, detail=f"No entry with hash:{hash} in the database processed_data_info")
    except exceptions.InvalidParameters:
        logger.error("Absent hash or type")
        return make_response(status_code=400, detail="Absent hash or type")
    except Exception as e:
        logger.exception(e)
        return make_response(status_code=500, detail=f"Something went wrong:\n{e}")


async def save_metadata(uof: PostgresUnitOfWork, **kwargs):
    try:
        async with uof:
            await uof.begin()
            await uof.custom_match_repo.save_test_matcher_metadata(**kwargs)
            await uof.commit()
            return make_response(result="Metadata successfully saved!")
    except Exception as e:
        logger.exception(e)
        return make_response(status_code=500, detail=f"Something went wrong:\n{e}")


async def get_results_custom(uof: PostgresUnitOfWork, task_id):
    """
            По task_id возвращает данные по ранам, параметры, и информацию о количестве событий и матчей
    :request: task_id
    :return: {
        status_code
        detail
        result: {
            runs: [],
            parameters: {},
            count: {},
            runtime: int}
    }
    """
    async with uof:
        try:
            await uof.begin()
            logger.info(f'start get_results_custom on task_id = {task_id}')
            runs_data = []
            runs = await uof.run_repo.get_by_task_id(task_id=task_id)
            matched_pair_count = 0
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
                    if is_match:
                        matched_pair_count += 1
                runs_res['results'] = results
                runs_data.append(runs_res)
            result = {}
            result['runs'] = runs_data

            test_matcher_metadata_result = await uof.custom_match_repo.get_test_matcher_metadata(task_id)
            result['parameters'] = {
                "remove_candidate_threshold": test_matcher_metadata_result[0][0],
                "confident_threshold": test_matcher_metadata_result[0][1],
                "minimal_sim_threshold": test_matcher_metadata_result[0][2],
                "final_sim_ratio": test_matcher_metadata_result[0][3],
            }
            result['count'] = {
                "bk1_event_count": test_matcher_metadata_result[0][4],
                "bk2_event_count": test_matcher_metadata_result[0][5],
                "all_event_count": test_matcher_metadata_result[0][6],
                "matched_pair_count": matched_pair_count
            }
            runtime_result = await uof.task_repo.get_by_id(task_id)
            result['runtime'] = str(runtime_result[2] - runtime_result[1])
            await uof.commit()
            logger.info(f'finish get_results_custom on task_id = {task_id}')
            return make_response(result=result)
        except Exception as e:
            await handle_error(uof, e)


def calculate_hash(json_data):
    sorted_data = json.dumps(json_data, sort_keys=True)
    sha256_hash = hashlib.sha256(sorted_data.encode()).hexdigest()
    return sha256_hash
