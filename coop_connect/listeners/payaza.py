import http.client
import json

from typing import Optional
from pydantic import BaseModel, Field
from coop_connect.root.connect_exception import ConnectBadRequestException

from coop_connect.root.settings import Settings
settings = Settings()

class PayazaVirtualAccountRequest(BaseModel):
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

class VirtualAccountData(BaseModel):
    account_name: str
    account_number: str
    account_type: str
    bank_name: str
    account_reference: str
    message: str

class PayazaResponse(BaseModel):
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



if __name__ == "__main__":
   resp = create_reserved_bank_account()