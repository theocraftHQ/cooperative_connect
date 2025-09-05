import logging
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, delete, extract, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

import coop_connect.schemas.finance_schemas as schemas
from coop_connect.database.orms.cooperative_orm import Wallet as WalletDB
from coop_connect.database.orms.cooperative_orm import ReservedBankAccount as ReservedBankAccountDB
from coop_connect.database.orms.cooperative_orm import Member as Member_DB
from coop_connect.root.database import async_session
from coop_connect.services.service_utils.exception_collection import (
    CreateError,
    DuplicateError,
    NotFound,
    UpdateError,
)

LOGGER = logging.getLogger(__name__)


# ------ WALLET ----------
async def create_wallet(
    wallet_in: schemas.Wallet,
):
    async with async_session() as session:
        stmt = (
            insert(WalletDB)
            .values(
                **wallet_in.model_dump(),
            )
            .returning(WalletDB)
        )
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()
        except IntegrityError as e:
            LOGGER.error(f"duplicate record found {wallet_in} - {e}")
            await session.rollback()
            raise DuplicateError
        if not result:
            LOGGER.error("Wallet creation Failed")
            await session.rollback()
            raise CreateError
        await session.commit()
        return schemas.WalletFull(**result.as_dict())

async def get_wallet(user_id: UUID, cooperative_id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(
                select(WalletDB).where(
                    and_(
                        WalletDB.user_id == user_id,
                        WalletDB.cooperative_id == cooperative_id,
                    )
                )
            )
        ).scalar_one_or_none()
        if not result:
            raise NotFound
        return schemas.WalletFull(**result.as_dict())

async def update_wallet(
    wallet_details: schemas.WalletUpdate,
    wallet_id: UUID

):
    async with async_session() as session:
        stmt = (
            update(WalletDB)
            .where(WalletDB.id == wallet_id)
            .values(
                wallet_details.model_dump(exclude_none=True, exclude_unset=True)
            )
            .returning(WalletDB)
        )
        result = (await session.execute(statement=stmt)).scalar_one_or_none()
        if not result:
            await session.rollback()
            raise UpdateError

        await session.commit()

        return schemas.WalletFull(**result.as_dict())
    
# ------ END OF WALLET ----------


# ------ BANK ACCOUNTS ----------
async def create_bank_account(
    bank_details: schemas.BankAccount,
):
    async with async_session() as session:
        stmt = (
            insert(ReservedBankAccountDB)
            .values(
                **bank_details.model_dump(),
            )
            .returning(ReservedBankAccountDB)
        )
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()
        except IntegrityError as e:
            LOGGER.error(f"duplicate record found {bank_details} - {e}")
            await session.rollback()
            raise DuplicateError
        if not result:
            LOGGER.error("Bank account creation Failed")
            await session.rollback()
            raise CreateError
        await session.commit()
        return schemas.BankAccountFull(**result.as_dict())

async def get_bank_account(user_id: UUID, cooperative_id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(
                select(ReservedBankAccountDB).where(
                    and_(
                        ReservedBankAccountDB.user_id == user_id,
                        ReservedBankAccountDB.cooperative_id == cooperative_id,
                    )
                )
            )
        ).scalar_one_or_none()
        if not result:
            raise NotFound
        return schemas.BankAccountFull(**result.as_dict())

async def update_bank_account(
    bank_details: schemas.BankAccountUpdate,
    user_id: UUID,
    cooperative_id: UUID
):
    async with async_session() as session:
        stmt = (
            update(ReservedBankAccountDB)
            .where(
                and_(
                        ReservedBankAccountDB.user_id == user_id,
                        ReservedBankAccountDB.cooperative_id == cooperative_id,
                    )
            )
            .values(
                bank_details.model_dump(exclude_none=True, exclude_unset=True)
            )
            .returning(ReservedBankAccountDB)
        )
        result = (await session.execute(statement=stmt)).scalar_one_or_none()
        if not result:
            await session.rollback()
            raise UpdateError

        await session.commit()

        return schemas.BankAccountFull(**result.as_dict())
# ------ END OF BANK ACCOUNTS ----------