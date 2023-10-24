import os
from dotenv import load_dotenv
load_dotenv(".env")

HOST_BACKEND = os.getenv('HOST_BACKEND', None)
INPUT_TOPIC = os.environ.get('INPUT_TOPIC', None)
INPUT_TOPIC_DATA = os.environ.get('INPUT_TOPIC_DATA', None)
CACHE_TOPIC = os.environ.get('CACHE_TOPIC', None)
OUTPUT_TOPIC = os.environ.get('OUTPUT_TOPIC', None)
OUTPUT_TOPIC_DATA = os.environ.get('OUTPUT_TOPIC_DATA', None)
KAFKA_HOST = os.environ.get('KAFKA_HOST', None)
CONSUMER_GROUP = os.environ.get('CONSUMER_GROUP', None)
PARTITION_NUMBER = os.environ.get('PARTITION_NUMBER', 1)
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', None)
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', None)
RABBITMQ_DEFAULT_USER = os.environ.get('RABBITMQ_DEFAULT_USER', None)
RABBITMQ_DEFAULT_PASS = os.environ.get('RABBITMQ_DEFAULT_PASS', None)

if not HOST_BACKEND:
    raise EnvironmentError("Missing env variable for backend host.")

if not (INPUT_TOPIC and OUTPUT_TOPIC and INPUT_TOPIC_DATA and CACHE_TOPIC):
    raise EnvironmentError("Missing topic names env variables.")

if not (KAFKA_HOST and CONSUMER_GROUP and PARTITION_NUMBER):
    raise EnvironmentError("Missing KAFKA env variables.")

if not (RABBITMQ_HOST and RABBITMQ_PORT and RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS):
    raise EnvironmentError("Missing RabbitMQ env variables.")
