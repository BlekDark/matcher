import src.request as request
from src.loader import get_data
from src.matcher import match
from config import OUTPUT_TOPIC, CACHE_TOPIC
from kafka import producer, send_2_rabbit
from threading import Thread
import time
import json
from typing import List, Dict, Optional
from collections import defaultdict
import logging
import datetime
import asyncio
import aio_pika

logger = logging.getLogger("event-matcher")

results = defaultdict(dict)
sources = request.get_sources()
sport_types = request.get_sport_types()
job_id = 0

async def proceed_match_async(source1_name: Optional[str],
                              source2_name: Optional[str],
                              sport_name: str,
                              is_cyber: str,
                              task_id: int,
                              run_id: int,
                              events1: List,
                              events2: List,
                              events1_ids: List,
                              events2_ids: List,
                              parameters: Dict[str, float],
                              whitelist: List[Dict],
                              banlist: List[Dict],
                              inplace_data: bool):
    global results, sport_types, sources
    try:
        info = {"bk1": source1_name,
                "bk2": source2_name,
                "sport": sport_name,
                "is_cyber": is_cyber,
                "task_id": task_id,
                "run_id": run_id}
        t1 = time.time()
        pairs = await match(events1, events2, parameters, info, whitelist, banlist, to_output_data=inplace_data)
        t2 = time.time()

        t = round((t2 - t1), 4)

        logger.info(f"OK. Matching run_id={run_id} in task_id={task_id} DONE. "
              f"Time: {round(t / 60, 3)} min.")

        result = {"status_code": 200,
                  "reason": "OK",
                  "bk1": source1_name,
                  "bk2": source2_name,
                  "sport": sport_name,
                  "is_cyber": is_cyber,
                  "task_id": task_id,
                  "run_id": run_id,
                  "runtime": t,
                  "result": pairs}
        # producer.produce(OUTPUT_TOPIC, value=json.dumps(result))
        await send_2_rabbit(json.dumps(result), to_output_data=inplace_data)
        timestamp = datetime.datetime.now().timestamp()
        cache_data =  {"result": result,
                       "timestamp": timestamp,
                       "events_ids":
                           {
                               source1_name: events1_ids,
                               source2_name: events2_ids
                           }
                       }
        producer.produce(CACHE_TOPIC, value=json.dumps({'bk1': source1_name,
                                                        'bk2': source2_name,
                                                        'sport': sport_name,
                                                        'is_cyber': is_cyber,
                                                        'cache': cache_data}))
        producer.flush()
        request.finish_run(run_id=run_id, task_id=task_id, num_matches=len(pairs),
                           runtime=t, pairs=pairs)
    except Exception as e:
        result = {"status_code": 404,
                  "reason": str(e),
                  "bk1": source1_name,
                  "bk2": source2_name,
                  "sport": sport_name,
                  "is_cyber": is_cyber,
                  "task_id": task_id,
                  "run_id": run_id
                  }
        logger.error(f"{e}")
        await send_2_rabbit(json.dumps(result), to_output_data=inplace_data)


def proceed_match(source1_name: Optional[str],
                  source2_name: Optional[str],
                  sport_name: str,
                  is_cyber: str,
                  task_id: int,
                  run_id: int,
                  events1: List,
                  events2: List,
                  events1_ids: List,
                  events2_ids: List,
                  parameters: Dict[str, float],
                  whitelist: List[Dict],
                  banlist: List[Dict],
                  inplace_data: bool):
    asyncio.run(proceed_match_async(source1_name,
                                    source2_name,
                                    sport_name,
                                    is_cyber,
                                    task_id,
                                    run_id,
                                    events1,
                                    events2,
                                    events1_ids,
                                    events2_ids,
                                    parameters,
                                    whitelist,
                                    banlist,
                                    inplace_data))