from datetime import datetime
import http.client
import json
import hmac
import hashlib
import base64
import logging

from coop_connect.listeners import rabbitmq
from coop_connect.root.utils.base_schemas import AbstractModel
from coop_connect.root.connect_exception import ConnectAuthException, ConnectBadRequestException, ConnectReqPayloadException
from coop_connect.root.settings import Settings

from fastapi import Request
from fastapi.responses import JSONResponse


settings = Settings()

LOGGER = logging.getLogger(__name__)

class PayazaVirtualAccountRequest(AbstractModel):
    account_name: str
    account_type: str
    bank_code: str
    bvn: str
    bvn_validated: bool
    account_reference: str
    customer_first_name: str
    customer_last_name: str
    customer_email: str
    customer_phone_number: str

class VirtualAccountData(AbstractModel):
    account_name: str
    account_number: str
    account_type: str
    bank_name: str
    account_reference: str
    message: str

class PayazaResponse(AbstractModel):
    message: str
    data: VirtualAccountData
    success: bool

def create_reserved_bank_account(
      account_reference,
      cooperative,
      user
):
  conn = http.client.HTTPSConnection("api.payaza.africa")
  req = PayazaVirtualAccountRequest(
    account_name=f"{cooperative.acronym}/{user.first_name} {user.last_name}",
    account_type="Static",
    bank_code="1067",
    bvn=user.bio.bvn,
    bvn_validated=True,
    account_reference=account_reference,
    customer_first_name=user.first_name,
    customer_last_name=user.last_name,
    customer_email=user.email,
    customer_phone_number=user.phone_number
  )
  payload = req.model_dump_json()
  headers = {
    'Authorization': f'Payaza {settings.payaza_public_token}',
    'Content-Type': 'application/json'
  }
  try:
    conn.request("POST", "/live/merchant-collection/merchant/virtual_account/generate_virtual_account/", payload, headers)
    res = conn.getresponse()
    data = res.read()
    res_obj = json.loads(data.decode("utf-8"))
    return PayazaResponse.model_validate(res_obj)
  except Exception as e:
     raise ConnectBadRequestException(f"Payaza virtual bank account creation failed - {e}")

async def generate_hmac_signature(data: str, secret_key: str) -> str:
    signature = hmac.new(
        secret_key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha512
    )
    return base64.b64encode(signature.digest()).decode('utf-8')

async def verify_webhook_signature(payload: str, signature: str, secret_key: str) -> bool:
    computed_signature = await generate_hmac_signature(payload, secret_key)
    return hmac.compare_digest(computed_signature, signature)

async def process_payaza_request(request: Request):
  try:
      # Get raw request body
      raw_body = await request.body()
      payload = raw_body.decode('utf-8')
      
      # Get headers
      headers = dict(request.headers)
      
      # Extract signature from headers
      signature = headers.get('x-payaza-signature')
      if not signature:
          LOGGER.warning("Missing x-payaza-signature header")
          raise ConnectBadRequestException(message="Missing x-payaza-signature header")
      
      # Validate webhook signature
      if not verify_webhook_signature(payload, signature, settings.payaza_secret_key):
          LOGGER.warning("Invalid webhook signature")
          raise ConnectAuthException(message="Invalid webhook signature")
      
      # Parse the validated payload
      try:
          webhook_payload = json.loads(payload)
      except json.JSONDecodeError as e:
          LOGGER.error(f"Invalid JSON payload: {str(e)}")
          raise ConnectReqPayloadException(message="Invalid JSON payload")
      
      # Prepare data for RabbitMQ
      webhook_data = {
          "event_id": webhook_payload.get('id', f"webhook_{int(datetime.now().timestamp())}"),
          "event_type": webhook_payload.get('event'),
          "received_at": datetime.now().isoformat(),
          "signature_validated": True,
          "headers": {
              "user-agent": headers.get('user-agent'),
              "content-type": headers.get('content-type'),
              "x-payaza-signature": signature
          },
          "payload": webhook_payload,
          "raw_payload": payload
      }
      
      # Log basic info immediately
      LOGGER.info(
          f"Received valid Payaza webhook - Event: {webhook_data['event_type']}, "
          f"ID: {webhook_data['event_id']}"
      )
      
      # Add background task to publish to RabbitMQ
      await rabbitmq.publish_to_rabbitmq(webhook_data, 'payaza_incoming_payment')
      
      # Return success response to Payaza
      return JSONResponse(
          status_code=200,
          content={
              "status": "received",
              "message": "Webhook processed successfully",
              "timestamp": datetime.now().isoformat()
          }
      )
  except Exception as e:
      LOGGER.error(f"Unexpected error processing webhook: {str(e)}")
      raise ConnectBadRequestException(messgae=f"Unexpected error processing webhook: {str(e)}")


async def process_payaza_deposit():
    # call the deposit service from finance here
    pass

async def process_payaza_payment(message):
    # The idea is that this function will route processing to the difference function to handle deposit, tranfer or any other thing
    if message['event_type'] == 'payment.successful':
        await process_payaza_deposit(message)
    else:
        LOGGER.warning(f"Unknown event type: {message['event_type']}")

if __name__ == "__main__":
#  resp = create_reserved_bank_account()
    pass