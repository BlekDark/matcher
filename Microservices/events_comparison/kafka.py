from config import OUTPUT_TOPIC, OUTPUT_TOPIC_DATA, KAFKA_HOST, CONSUMER_GROUP, PARTITION_NUMBER, \
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_DEFAULT_PASS, RABBITMQ_DEFAULT_USER

from confluent_kafka import Consumer, Producer
import aio_pika

conf = {
    'bootstrap.servers': KAFKA_HOST,
    'group.id': CONSUMER_GROUP

}
producer = Producer({'bootstrap.servers': KAFKA_HOST})


async def send_2_rabbit(message, to_output_data=False):
    result_connection = await aio_pika.connect(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        login=RABBITMQ_DEFAULT_USER,
        password=RABBITMQ_DEFAULT_PASS)

    target_queue = OUTPUT_TOPIC_DATA if to_output_data else OUTPUT_TOPIC

    result_channel = await result_connection.channel()

    result_queue = await result_channel.get_queue(target_queue)
    if result_queue is None:
        queue_args = {'x-message-ttl': 60000}
        result_queue = await result_channel.declare_queue(target_queue, auto_delete=True, arguments=queue_args)

    await result_channel.default_exchange.publish(
        aio_pika.Message(body=message.encode()),
        routing_key=result_queue.name,
    )
    await result_connection.close()
