from typing import Any, Dict
import aio_pika
import logging
import json

LOGGER = logging.getLogger(__name__)

async def get_rabbitmq_channel(queue_name: str):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name, durable=True)
    LOGGER.info(' [*] Waiting for messages. To exit press CTRL+C')
    return channel, queue


async def publish_to_rabbitmq(message: Dict[str, Any], queue_name: str):
    """
    Publishes webhook data to RabbitMQ queue
    
    Args:
        message (dict): The webhook data to publish
        queue_name (str): Name of the RabbitMQ queue
    """
    try:
        # Connect to RabbitMQ
        channel, queue = await get_rabbitmq_channel(queue_name)
        
        # Prepare message
        message_body = json.dumps(message, default=str)
        rabbitmq_message = aio_pika.Message(message_body.encode('utf-8'), delivery_mode=aio_pika.DeliveryMode.PERSISTENT)
        
        # Publish message
        await channel.default_exchange.publish(rabbitmq_message, routing_key=queue)
        
        LOGGER.info(f"Successfully published webhook to RabbitMQ queue: {queue_name}")
        
        # Close connection
        
    except Exception as e:
        LOGGER.error(f"Failed to publish to RabbitMQ: {str(e)}")
        raise
