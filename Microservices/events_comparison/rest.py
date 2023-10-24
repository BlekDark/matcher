from collections import defaultdict
from typing import List, Dict, Optional
from threading import Thread
from src.loader import get_data, get_data_from_custom_json
from src.matcher import match, check_events
import src.request as request
from fastapi import FastAPI, HTTPException, Request
import uvicorn
import time
import logging
import asyncio
import concurrent.futures


logger = logging.getLogger("event-matcher")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s|%(levelname)s| %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()

# sources = request.get_sources()
# sport_types = request.get_sport_types()

job_id = 0

logger.info("Matcher started.")


async def proceed_match_async(source1_name: Optional[str],
                              source2_name: Optional[str],
                              sport_name: str,
                              is_cyber: str,
                              task_id: int,
                              run_id: int,
                              events1: List,
                              events2: List,
                              parameters: Dict[str, float],
                              whitelist: List[Dict],
                              banlist: List[Dict]):
    global sport_types, sources
    try:

        info = {"bk1": source1_name,
                "bk2": source2_name,
                "sport": sport_name,
                "is_cyber": is_cyber,
                "task_id": task_id,
                "run_id": run_id}
        t1 = time.time()
        pairs = await match(events1, events2, parameters, info, whitelist, banlist)
        t2 = time.time()

        t = round((t2 - t1), 4)

        logger.info(f"OK. Matching run_id={run_id} in task_id={task_id} DONE. "
              f"Time: {round(t / 60, 3)} min.")

        request.finish_run(run_id=run_id, task_id=task_id, num_matches=len(pairs),
                           runtime=t, pairs=pairs)
    except Exception as e:
        logger.error(f"Something went wrong: {e}")


async def proceed_match(source1_name: Optional[str],
                        source2_name: Optional[str],
                        sport_name: str,
                        is_cyber: str,
                        task_id: int,
                        run_id: int,
                        events1: List,
                        events2: List,
                        parameters: Dict[str, float],
                        whitelist: List[Dict],
                        banlist: List[Dict]):
    await proceed_match_async(source1_name,
                              source2_name,
                              sport_name,
                              is_cyber,
                              task_id,
                              run_id,
                              events1,
                              events2,
                              parameters,
                              whitelist,
                              banlist)



async def proceed_check_async(source1_name: Optional[str],
                              source2_name: Optional[str],
                              sport_name: str,
                              is_cyber: str,
                              events1: List,
                              events2: List,
                              parameters: Dict[str, float]):
    global sport_types
    try:

        all_event_ids = set(event['event_id'] for event in events1 + events2)

        t1 = time.time()
        pairs = await check_events(events1, events2, parameters, sport_name, is_cyber)
        t2 = time.time()

        for pair in pairs:
            all_event_ids.discard(pair['event1']['event_id'])
            all_event_ids.discard(pair['event2']['event_id'])

        unmatched_event_ids = all_event_ids

        t = round((t2 - t1), 4)

        logger.info(f"OK. Matching DONE. Time: {round(t / 60, 3)} min.")
        return pairs, list(unmatched_event_ids)
    except Exception as e:
        logger.error(f"Something went wrong: {e}")


def proceed_check(source1_name: Optional[str],
                  source2_name: Optional[str],
                  sport_name: str,
                  is_cyber: str,
                  events1: List,
                  events2: List,
                  parameters: Dict[str, float]):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(proceed_check_async(source1_name,
                                                           source2_name,
                                                           sport_name,
                                                           is_cyber,
                                                           events1,
                                                           events2,
                                                           parameters))
    finally:
        loop.close()


@app.get("/match/")
def run_match(one: str, two: str):
    global job_id, sources, sport_types
    try:
        if one == two:
            return HTTPException(status_code=404,
                                 detail="Matching the same source is forbidden!")
        if not (sources.get(one, None) and sources.get(two, None)):
            return HTTPException(status_code=404,
                                 detail="Unknown source was given! Register it in database and try again.")
        source1 = sources.get(one)
        source2 = sources.get(two)
        data, (status, reason) = get_data(source1, source2)
        if not status:
            return HTTPException(status_code=404,
                                 detail=reason)

        current_types = []
        for sport_name, d in data.items():
            for is_cyber, events in d.items():
                sport = sport_name + '-cyber=' + is_cyber
                current_types.append(sport)
        logger.info(f"{len(current_types)} sport types were found: {current_types}")
        sport_ids = {}
        for sport_name, d in data.items():
            for is_cyber, events in d.items():
                events1 = events.get(source1[0], [])
                events2 = events.get(source2[0], [])
                sport = sport_name + '-cyber=' + is_cyber
                if len(events1) != 0 and len(events2) != 0:
                    sport_id = sport_types.get(sport_name, {}).get(str(is_cyber), None)
                    if sport_id is None:
                        sport_id = request.add_sport_type(sport_name=sport_name, is_cyber=is_cyber)
                        sport_types[sport_name][str(is_cyber)] = sport_id
                    sport_ids[sport_id] = events
        task_id, run_ids = request.create_task(source1_id=source1[0], source2_id=source2[0], sport_ids=sport_ids)
        configuration = request.get_configuration(source1_id=source1[0], source2_id=source2[0])
        whitelist, banlist = request.get_manual_matches()
        base_configuration = {
            "MINIMAL_SIM_THRESHOLD": configuration.get("MINIMAL_SIM_THRESHOLD"),
            "REMOVE_CANDIDATE_THRESHOLD": configuration.get("REMOVE_CANDIDATE_THRESHOLD"),
            "FINAL_SIM_RATIO": configuration.get("FINAL_SIM_RATIO"),
            "CONFIDENT_THRESHOLD": configuration.get("CONFIDENT_THRESHOLD")
        }

        for sport_name, d in data.items():
            for is_cyber, events in d.items():
                sport = sport_name + '-cyber=' + is_cyber
                sport_id = sport_types.get(sport, None)
                if sport_id in sport_ids.keys():
                    run_id = run_ids.get(str(sport_id))
                    if configuration['types'].get(str(sport_id), None) is None:
                        run_configuration = base_configuration
                    else:
                        run_configuration = configuration['types'].get(str(sport_id))
                    events1 = events.get(source1[0], [])
                    events2 = events.get(source2[0], [])
                    logger.info(
                        f"Run algorithm for {sport_name} (cyber={is_cyber}). task_id={task_id}| run_id={run_id}")
                    Thread(target=proceed_match,
                           args=(one,
                                 two,
                                 sport_name,
                                 task_id,
                                 run_id,
                                 events1,
                                 events2,
                                 run_configuration,
                                 whitelist,
                                 banlist)).start()
        return {"status_code": 200, "task_id": task_id,
                "detail": f"OK. Matching between {one} & {two} has started!"}
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Something went wrong: {e}")


@app.post("/match_data/")
async def match_data(req: Request):
    """

    :param req:
    format: { referent_task_id: int,
              source1_id: int,
              source2_id: int,
              source1_data: List[json],
              source2_data: List[json],
              parameters: Dict[...]
            }
    :return:
    """
    global job_id, sport_types
    try:
        rawdata = await req.json()
        logger.info(f"Test Matching task for sources {rawdata.get('source1_id')} & {rawdata.get('source2_id')}"
                    f" for referent task={rawdata.get('referent_task_id')}")
        data, (status, reason) = get_data(source1=(rawdata.get('source1_id'), ''),
                                          source2=(rawdata.get('source2_id'), ''),
                                          rawdata1=rawdata.get('source1_data'),
                                          rawdata2=rawdata.get('source2_data'))
        if not status:
            return HTTPException(status_code=404,
                                 detail=reason)

        current_types = list(data.keys())
        logger.info(f"{len(current_types)} sport types were found: {current_types}")

        parameters = rawdata.get("parameters")
        base_configuration = {
            "MINIMAL_SIM_THRESHOLD": parameters.get("MINIMAL_SIM_THRESHOLD"),
            "REMOVE_CANDIDATE_THRESHOLD": parameters.get("REMOVE_CANDIDATE_THRESHOLD"),
            "FINAL_SIM_RATIO": parameters.get("FINAL_SIM_RATIO"),
            "CONFIDENT_THRESHOLD": parameters.get("CONFIDENT_THRESHOLD")
        }
        sport_ids = {}
        for sport_name, d in data.items():
            for is_cyber, events in d.items():
                events1 = events.get(rawdata.get('source1_id'), [])
                events2 = events.get(rawdata.get('source2_id'), [])
                sport = sport_name + '-cyber=' + is_cyber
                if len(events1) != 0 and len(events2) != 0:
                    sport_id = sport_types.get(sport_name, {}).get(str(is_cyber), None)
                    if sport_id is None:
                        sport_id = request.add_sport_type(sport_name=sport_name, is_cyber=is_cyber)
                        sport_types[sport_name][str(is_cyber)] = sport_id
                    sport_ids[sport_id] = events
        task_id, run_ids = request.create_task(source1_id=rawdata.get('source1_id'),
                                               source2_id=rawdata.get('source2_id'),
                                               sport_ids=sport_ids, referent_task=rawdata.get('referent_task_id'))
        if request.save_test_matcher_metadata(task_id, base_configuration, rawdata.get('source1_data'), rawdata.get('source2_data')):
            logger.info('Test match metadata successfully saved')
        whitelist, banlist = [], []

        for sport_name, d in data.items():
            for is_cyber, events in d.items():
                sport = sport_name + '-cyber=' + is_cyber
                sport_id = sport_types.get(sport_name, {}).get(str(is_cyber), None)
                if sport_id in sport_ids.keys():
                    run_id = run_ids.get(str(sport_id))
                    if parameters.get('types').get(str(sport_id), None) is not None:
                        run_configuration = parameters.get('types').get(str(sport_id))
                    else:
                        run_configuration = base_configuration
                    events1 = events.get(rawdata.get('source1_id'), [])
                    events2 = events.get(rawdata.get('source2_id'), [])
                    logger.info(
                        f"Run algorithm for {sport_name} (cyber={is_cyber}). task_id={task_id}| run_id={run_id}")
                    await proceed_match(None,
                                        None,
                                        sport_name,
                                        is_cyber,
                                        task_id,
                                        run_id,
                                        events1,
                                        events2,
                                        run_configuration,
                                        whitelist,
                                        banlist)
        return {"status_code": 200, "task_id": task_id,
                "detail": f"OK. Test matching between {rawdata.get('source1_id')} & {rawdata.get('source2_id')} "
                          f"has finished!"}
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Something went wrong: {e}")


@app.post("/check_quality/")
async def check_quality(req: Request):
    """
    Matching obviously correct pairs

    Args:
        req (Request): The request object.

    Request Body:
        {
            "bk1": {
                "data": [
                    {
                        "event_id": str(uuid4),
                        "sport": str,
                        "event_name": str,
                        "team1": str,
                        "team2": str,
                        "league_name": str,
                        "is_cyber": bool
                    },
                ]
            },
            "bk2": {
                "data": [
                    {
                        "event_id": str(uuid4),
                        "sport": str,
                        "event_name": str,
                        "team1": str,
                        "team2": str,
                        "league_name": str,
                        "is_cyber": bool
                    },
                ]
            }
        }

    Returns:
        dict: Matching result.
    """
    global sport_types
    try:
        data = await req.json()
        data, (status, reason) = get_data_from_custom_json(rawdata1=data.get('bk1').get('data'),
                                                           rawdata2=data.get('bk2').get('data'))

        parameters = request.get_parameters()
        base_configuration = {
            "MINIMAL_SIM_THRESHOLD": parameters.get("MINIMAL_SIM_THRESHOLD"),
            "REMOVE_CANDIDATE_THRESHOLD": parameters.get("REMOVE_CANDIDATE_THRESHOLD"),
            "FINAL_SIM_RATIO": parameters.get("FINAL_SIM_RATIO"),
            "CONFIDENT_THRESHOLD": parameters.get("CONFIDENT_THRESHOLD")
        }


        current_types = []
        for sport_name, d in data.items():
            for is_cyber, events in d.items():
                sport = sport_name + '-cyber=' + is_cyber
                current_types.append(sport)
        logger.info(f"{len(current_types)} sport types were found: {current_types}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = []

            matched_pairs = []
            unmatched_events = []

            actual_runs = 0
            for sport_name, d in data.items():
                for is_cyber, events in d.items():
                    actual_runs += 1
                    events1 = events.get('bk1', [])
                    events2 = events.get('bk2', [])
                    task = loop.run_in_executor(executor,
                                                proceed_check,
                                                'bk1',
                                                'bk2',
                                                sport_name,
                                                is_cyber,
                                                events1,
                                                events2,
                                                base_configuration)
                    tasks.append(task)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error: {result}")
                else:
                    pairs, unmatched = result
                    matched_pairs.extend(pairs)
                    unmatched_events.extend(unmatched)
            check_result = {
                'matched_pairs': matched_pairs,
                'unmatched_events': unmatched_events}



        logger.info('Quality check successfully completed')
        return {"status_code": 200, "detail": f"OK. Quality check completed", "check_result": check_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {e}")


@app.post("/revers_match/")
async def revers_match(req: Request):
    """
    :param req:
    format:
        [{
            event1: dict, event2: dict
        }, ...]
    :return: {
        "final_sim_ratio": float,
        "minimal_sim_threshold": float,
        "remove_candidate_threshold": float,
        "confident_threshold": float
    }
    """
    data = await req.json()
    result = get_parameters_match(data)
    return {"status_code": 200, "result": result,
            "detail": f"parameters matcher successfully found"}


@app.get("/get_task_by_id/")
async def get_task_by_id(task_id):
    """

    """
    try:
        result = request.get_task_by_id(task_id)

        return {"status_code": 200, "result": result,
                "detail": f"parameters matcher successfully found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {e}")

if __name__ == "__main__":
    uvicorn.run(app)
