from typing import List, Dict
import schedule
import time
import os
from dotenv import load_dotenv
import pika
import json
import logging
import asyncio
import yaml
load_dotenv(".env")

logger = logging.getLogger("task-scheduler")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s|%(levelname)s| %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

INPUT_TOPIC = os.environ.get('INPUT_TOPIC', None)
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', None)
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', None)
RABBITMQ_DEFAULT_USER = os.environ.get('RABBITMQ_DEFAULT_USER', None)
RABBITMQ_DEFAULT_PASS = os.environ.get('RABBITMQ_DEFAULT_PASS', None)
REGULARITY = int(os.environ.get('REGULARITY', None))


if not INPUT_TOPIC:
    raise EnvironmentError("Missing topic name env variables.")


if not (RABBITMQ_HOST and RABBITMQ_PORT and RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS):
    raise EnvironmentError("Missing RabbitMQ env variables.")

def read_values():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    tasks = []
    for bk1, bk2 in config['sources']:
        task = {
            'bk1': bk1,
            'bk2': bk2,
            'use_cache': True
        }
        tasks.append(task)
    return tasks

tasks: List[Dict] = read_values()

def send_tasks():
    credentials = pika.PlainCredentials(RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT,
                                                                   credentials=credentials))
    logger.info(10 * "---")
    channel = connection.channel()
    arguments = {'x-message-ttl' : 60000}
    channel.queue_declare(queue=INPUT_TOPIC, durable=True, arguments=arguments)
    for message in tasks:

        channel.basic_publish(exchange='',
                              routing_key=INPUT_TOPIC,
                              body=str(message),
                              properties=pika.BasicProperties(content_type='text/plain',
                                                              delivery_mode=pika.DeliveryMode.Transient,
                                                              expiration='60000'),
                              mandatory=True
                              )
        logger.info(f"The task for matching {message.get('bk1')}&{message.get('bk2')} sent successfully.")
    logger.info(10 * "---")
    logger.info("Waiting...")
    connection.close()


logger.info("Task sender is initialized.")
schedule.every(REGULARITY).seconds.do(send_tasks)
while True:
    schedule.run_pending()
    time.sleep(1)
