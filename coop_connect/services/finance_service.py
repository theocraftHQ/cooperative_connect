import logging
from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

import coop_connect.database.db_handlers.finance_db_handler as finance_db_handler
import coop_connect.schemas.finance_schemas as schemas
import coop_connect.schemas.cooperative_schemas as cooperative_schemas
from coop_connect.root.connect_exception import (
    ConnectBadRequestException,
    ConnectNotFoundException,
)
from coop_connect.schemas.user_schemas import UserProfile
from coop_connect.services.service_utils.exception_collection import (
    NotFound,
    UpdateError,
)

from coop_connect.services import payaza_service

LOGGER = logging.getLogger(__name__)

async def _get_member_wallet(user_id: UUID, cooperative_id: UUID):
    try:
        return await finance_db_handler.get_wallet(
            user_id=user_id, cooperative_id=cooperative_id
        )
    except NotFound as e:
        raise e
    
# call this function immediately a member status is set to active.
async def create_member_wallet(
    cooperative: cooperative_schemas.CooperativeProfile,
    user: UserProfile,
):
    try:
        await _get_member_wallet(
            user_id=user.id, cooperative_id=cooperative.id
        )
        raise ConnectBadRequestException(
            message="Wallet already exist for this member"
        )
    except NotFound:
        return await finance_db_handler.create_wallet(
            wallet_in=schemas.Wallet(
                user_id=user.id,
                currency_code="NGN",
                cooperative_id=cooperative.id
            )
        )

async def update_wallet(
        wallet_update: schemas.WalletUpdate,
        cooperative: cooperative_schemas.CooperativeProfile,
        user: UserProfile
    ):
    # if wallet_update.is_active is None:

    wallet= await _get_member_wallet(
            user_id=user.id, cooperative_id=cooperative.id
        )
    return await finance_db_handler.update_wallet(
        wallet_details=wallet_update, wallet_id=wallet.id
    )


async def _get_bank_account(user_id: UUID, cooperative_id: UUID):
    try:
        return await finance_db_handler.get_bank_account(
            user_id=user_id, cooperative_id=cooperative_id
        )
    except NotFound as e:
        raise e

async def create_member_bank_account(
    cooperative: cooperative_schemas.CooperativeProfile,
    user: UserProfile,
    provider: str = "PAYAZA",
):
    try:
        await _get_bank_account(
            user_id=user.id, cooperative_id=cooperative.id
        )
        raise ConnectBadRequestException(
            message="Bank account already exist for this member"
        )
    except NotFound:
        account_reference = f"ref_{cooperative.acronym}_{user.id}"
        if provider == "PAYAZA":
            from_provider_deatils = payaza_service.create_reserved_bank_account(
                account_reference,
                cooperative,
                user
            )
        elif provider == "BUDPAY":
            pass
        elif provider == "PAYVESSEL":
            pass
        else:
            raise ConnectBadRequestException(
            message="Wrong Virtual Account Provder Supplied"
        )
        return await finance_db_handler.create_bank_account(
            bank_details=schemas.BankAccount(
                **from_provider_deatils.data,
                provider=provider,
                user_id=user.id,
                cooperative_id=cooperative.id,
                meta=from_provider_deatils.model_dump_json()
            )
        )
    

async def payaza_collect_payment(
        wallet_update: schemas.WalletUpdate,
        cooperative: cooperative_schemas.CooperativeProfile,
        user: UserProfile
    ):
    # if wallet_update.is_active is None:

    wallet= await _get_member_wallet(
            user_id=user.id, cooperative_id=cooperative.id
        )
    return await finance_db_handler.update_wallet(
        wallet_details=wallet_update, wallet_id=wallet.id
    )