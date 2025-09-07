from datetime import date, datetime
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import AnyHttpUrl, EmailStr, Field, conint

from coop_connect.root.coop_enums import (
    CooperativeStatus,
    CooperativeUserRole,
    MembershipStatus,
    MembershipType,
)
from coop_connect.root.utils.base_schemas import (
    AbstractModel,
    CoopInt,
    PaginationModel,
    PhoneNumber,
)


class Wallet(AbstractModel):
    user_id: UUID
    currency_code: str
    cooperative_id: UUID

class WalletUpdate(AbstractModel):
    balance: str
    is_active: Optional[str] = None

class WalletFull(Wallet):
    id: UUID
    balance: str
    is_active: bool
    meta: dict

class BankAccount(AbstractModel):
    user_id: UUID
    cooperative_id: UUID
    account_name: str
    account_number: str
    bank_code: str
    bank_name: str
    currency_code: str = "NGN"
    provider: str
    account_reference: str
    meta: dict

class BankAccountUpdate(AbstractModel):
    status: str

class BankAccountFull(BankAccount):
    id: UUID
    status: str
    

