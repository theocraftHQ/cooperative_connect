from datetime import datetime
from typing import Any, Dict
import aio_pika
from aio_pika.abc import AbstractIncomingMessage
import logging
import json
from coop_connect.services.payaza_service import process_payaza_payment

LOGGER = logging.getLogger(__name__)

async def get_rabbitmq_channel(queue_name: str):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/") # I think this needs to be on_start of the app.
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


async def consume_from_rabbitmq(message: AbstractIncomingMessage):
    # Need to tell this guy the queue to consume from.
    # I want to make this a generic interface for consuming messages from the queue and calling the
    # function responsible for processing it. This might be a bad idea but I don't know yet
    # and I think it depends on whether we want to have a single queue per payment provider, or a single queue for just processing payments across all providers
    try:
        msg = json.loads(message.body.decode('utf-8'))
        payload = msg.get('payload', {})
        event_type = payload.get('event')
        data = payload.get('data', {})
        
        # Extract key information
        transaction_id = data.get('transaction_id') or data.get('id')
        reference = data.get('reference')
        amount = data.get('amount')
        currency = data.get('currency')
        status = data.get('status')
        customer = data.get('customer', {})
        
        LOGGER.info(f"Processing {event_type} for transaction {transaction_id}")
        
        processing_result = {
            'transaction_id': transaction_id,
            'reference': reference,
            'amount': amount,
            'currency': currency,
            'status': status,
            'event_type': event_type,
            'processed_at': datetime.now().isoformat(),
            'customer_email': customer.get('email'),
            'success': False,
            'action_taken': None,
            'error': None
        }
        
        # Process based on event type
        
        result = await process_payaza_payment(processing_result)

        LOGGER.info(f"Processed [X] event {result}")

        return processing_result
        
    except Exception as e:
        LOGGER.error(f"Error processing payment event: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'action_taken': None,
            'processed_at': datetime.now().isoformat()
        }
