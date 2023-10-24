from rest import app
from config import KAFKA_HOST, INPUT_TOPIC,  INPUT_TOPIC_DATA, OUTPUT_TOPIC, CACHE_TOPIC, OUTPUT_TOPIC_DATA, \
    PARTITION_NUMBER, CONSUMER_GROUP, RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_DEFAULT_PASS, RABBITMQ_DEFAULT_USER
from match_logic import proceed_match
from kafka import producer, send_2_rabbit
import src.request as request
from src.loader import get_data

import ast
import json
from typing import List
from threading import Thread
import logging
from collections import defaultdict
import uuid
import asyncio

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer, Producer
import aio_pika
from aio_pika.exceptions import QueueEmpty
from aiormq.exceptions import ChannelNotFoundEntity
import uvicorn

logger = logging.getLogger("event-matcher")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s|%(levelname)s| %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

sources = request.get_sources()
sport_types = request.get_sport_types()

def get_events_ids(events: List):
    return [str(e['bk_event_id']) for e in events]

class MatcherApplication:
    def __init__(self, bootstrap_servers: str,
                       task_input_topic: str,
                       task_input_data_topic: str,
                       data_cache_topic: str,
                       output_topic: str,
                       output_data_topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.task_input_topic = task_input_topic
        self.task_input_data_topic = task_input_data_topic
        self.data_cache_topic = data_cache_topic
        self.output_topic = output_topic
        self.cache = defaultdict(lambda: defaultdict(dict))
        self.output_data_topic = output_data_topic
        self.running = True

        # Create consumer and producer instances
        self.task_input_consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': CONSUMER_GROUP
        })
        self.data_cache_consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id':  str(uuid.uuid4())
        })


    def is_cache_relevant(self, bk1: str, bk2: str, sport: str, events1: List, events2: List):
        if sport in self.cache[bk1][bk2].keys() and len(self.cache[bk1][bk2][sport]) != 0:
            events_ids1 = set(get_events_ids(events1))
            events_ids2 = set(get_events_ids(events2))
            cache_event_ids1 = set(self.cache[bk1][bk2][sport]['events_ids'][bk1])
            cache_event_ids2 = set(self.cache[bk1][bk2][sport]['events_ids'][bk2])
            return events_ids1 == cache_event_ids1 and events_ids2 == cache_event_ids2
        return False

    async def run_match(self, message, inplace_data=False):
        result = {}
        try:
            if inplace_data:
                bk1 = message.get('bk1').get('name')
                bk2 = message.get('bk2').get('name')
            else:
                bk1 = message.get('bk1')
                bk2 = message.get('bk2')
            use_cache = bool(message.get('use_cache', True))
            logger.info(f"Matching task for sources: {bk1} & {bk2}")
            if bk1 == bk2:
                result['status_code'] = 404
                result['reason'] = "Matching the same source is forbidden!"
                logger.error("Matching the same source is forbidden!")

                await send_2_rabbit(json.dumps(result), to_output_data=inplace_data)

                return
            if not (sources.get(bk1, None) and sources.get(bk2, None)):
                result['status_code'] = 404
                result['reason'] = "Unknown source was given! Register it in database and try again."
                logger.error("Unknown source was given! Register it in database and try again.")
                await send_2_rabbit(json.dumps(result), to_output_data=inplace_data)
                return
            source1 = sources.get(bk1)
            source2 = sources.get(bk2)
            if inplace_data:
                data, (status, reason) = get_data(source1=source1,
                                                  source2=source2,
                                                  rawdata1=message.get('bk1').get('data'),
                                                  rawdata2=message.get('bk2').get('data'))
            else:
                data, (status, reason) = get_data(source1, source2)
            if not status:
                result['status_code'] = 404
                result['reason'] = reason
                logger.error(f"{reason}")
                await send_2_rabbit(json.dumps(result), to_output_data=inplace_data)
                return
            configuration = request.get_configuration(source1_id=source1[0], source2_id=source2[0])
            whitelist, banlist = request.get_manual_matches()
            base_configuration = {
                "MINIMAL_SIM_THRESHOLD": configuration.get("MINIMAL_SIM_THRESHOLD"),
                "REMOVE_CANDIDATE_THRESHOLD": configuration.get("REMOVE_CANDIDATE_THRESHOLD"),
                "FINAL_SIM_RATIO": configuration.get("FINAL_SIM_RATIO"),
                "CONFIDENT_THRESHOLD": configuration.get("CONFIDENT_THRESHOLD")
            }
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
                    if use_cache and self.is_cache_relevant(bk1, bk2, sport, events1, events2):
                        cache = self.cache[bk1][bk2][sport]
                        res = cache.get('result')
                        res['reason'] = 'Cached data'
                        await send_2_rabbit(json.dumps(res), to_output_data=inplace_data)
                        logger.info(f'--- produced cache for sport {sport_name} (cyber={is_cyber}) ---')
                    elif len(events1) != 0 and len(events2) != 0:
                        self.cache[bk1][bk2][sport] = {}
                        self.cache[bk2][bk1][sport] = {}
                        sport_id = sport_types.get(sport_name, {}).get(str(is_cyber), None)
                        if sport_id is None:
                            sport_id = request.add_sport_type(sport_name=sport_name, is_cyber=is_cyber)
                            sport_types[sport_name][str(is_cyber)] = sport_id
                        sport_ids[sport_id] = events
            task_id, run_ids = request.create_task(source1_id=source1[0],
                                                   source2_id=source2[0],
                                                   sport_ids=sport_ids)
            all_runs = len(current_types)
            actual_runs = 0
            for sport_name, d in data.items():
                for is_cyber, events in d.items():
                    sport_id = sport_types.get(sport_name, {}).get(str(is_cyber))
                    if sport_id in sport_ids.keys():
                        actual_runs += 1
                        run_id = run_ids.get(str(sport_id))
                        if configuration['types'].get(str(sport_id), None) is None:
                            run_configuration = base_configuration
                        else:
                            run_configuration = configuration['types'].get(str(sport_id))
                        events1 = events.get(source1[0], [])
                        events1_ids = get_events_ids(events1)
                        events2 = events.get(source2[0], [])
                        events2_ids = get_events_ids(events2)
                        logger.info(f"Run algorithm for {sport_name} (cyber={is_cyber}). task_id={task_id}| run_id={run_id}")
                        Thread(target=proceed_match,
                               args=(bk1,
                                     bk2,
                                     sport_name,
                                     is_cyber,
                                     task_id,
                                     run_id,
                                     events1,
                                     events2,
                                     events1_ids,
                                     events2_ids,
                                     run_configuration,
                                     whitelist,
                                     banlist,
                                     inplace_data)).start()
            logger.info(
                f'Matching {bk1}&{bk2} is processing. Total sports: {all_runs} => (Algo={actual_runs} and Cache={all_runs - actual_runs})')
        except Exception as e:
            logger.error(f"Something went wrong with message:\n{message}\n Error:{e}")
            result['status_code'] = 404
            result['reason'] = str(e)
            await send_2_rabbit(json.dumps(result), to_output_data=inplace_data)

    async def connect_queue(self, queue_name: str):
        # RabbitMQ connection settings
        connection = await aio_pika.connect(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            login=RABBITMQ_DEFAULT_USER,
            password=RABBITMQ_DEFAULT_PASS,
            timeout=60000)

        channel = await connection.channel()

        try:
            queue = await channel.get_queue(queue_name)
        except (QueueEmpty, ChannelNotFoundEntity) as e:
            logger.error(e, exc_info=True)
            logger.info('Trying to declare queue..')
            channel = await connection.channel()
            queue_args = {'x-message-ttl': 60000}
            queue = await channel.declare_queue(queue_name, durable=True, arguments=queue_args)
            logger.info(f'Queue "{queue_name}" has been declared.')
        return queue

    async def consume_task_input_queue(self):

        queue = await self.connect_queue(self.task_input_topic)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    # logger.info(f"Received message: {message.body.decode()}")
                    data = ast.literal_eval(message.body.decode())
                    await self.run_match(data)

    async def consume_task_input_queue_data(self):

        queue = await self.connect_queue(self.task_input_data_topic)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = message.body
                    if isinstance(data, bytes):
                        data = data.decode()
                    try:
                        data = ast.literal_eval(data)
                    except (ValueError, SyntaxError):
                        pass
                    if isinstance(data, str):
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError:
                            logger.error('An error occured on json.loads(data)')
                    await self.run_match(data, inplace_data=True)

    async def consume_data_cache(self):
        self.data_cache_consumer.subscribe([self.data_cache_topic])

        while self.running:
            msg = self.data_cache_consumer.poll(1.0)

            if msg is None:
                await asyncio.sleep(0.01)
                continue
            if msg.error():
                logging.error(f'Consumer error: {msg.error()}')
                continue

            message = json.loads(msg.value().decode('utf-8'))
            try:
                bk1 = message.get('bk1')
                bk2 = message.get('bk2')
                sport_name = message.get('sport')
                is_cyber = message.get('is_cyber')
                cache = message.get('cache')
                sport = sport_name + '-cyber=' + is_cyber
                self.cache[bk1][bk2][sport] = cache
                self.cache[bk2][bk1][sport] = cache
                logger.info(f'Updated local cache for {bk1} & {bk2} for {sport_name} (cyber={is_cyber})')

            except Exception as e:
                logger.error(f"Something went wrong with message:\n{message}\n Error:{e}")
            self.data_cache_consumer.commit()


core_matcher = MatcherApplication(KAFKA_HOST, INPUT_TOPIC, INPUT_TOPIC_DATA, CACHE_TOPIC, OUTPUT_TOPIC, OUTPUT_TOPIC_DATA)


async def start_application():
    loop = asyncio.get_running_loop()
    tasks = [loop.create_task(core_matcher.consume_task_input_queue()),
             loop.create_task(core_matcher.consume_task_input_queue_data()),
             loop.create_task(core_matcher.consume_data_cache())]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    # uvicorn.run(app)
    logger.removeHandler(logger.handlers[1])
    logger.info("Matcher started.")
    asyncio.run(start_application())
