import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException

import theocraft_coop.database.db_handlers.cooperative_db_handler as cooperative_db_handler

LOGGER = logging.getLogger(__name__)

async def get_cooperative(id: UUID):
    try:
        return await cooperative_db_handler.get_coop(db_coop_id=id)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("user not found")

        raise TheocraftNotFoundException(message="Cooperative not found")
    
async def get_cooperative_user(id: UUID):
    try:
        return await cooperative_db_handler.get_coop_user(coop_user_id=id)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("user not found")

        raise TheocraftNotFoundException(message="Cooperative user not found")
    
async def get_cooperative_member(id: UUID):
    try:
        return await cooperative_db_handler.get_coop_member(coop_user_id=id)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("user not found")

        raise TheocraftNotFoundException(message="Cooperative member not found")