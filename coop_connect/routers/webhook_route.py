from uuid import UUID

from fastapi import APIRouter, Depends, status, Request

import coop_connect.schemas.cooperative_schemas as schemas
from coop_connect.services import payaza_service
from coop_connect.root.dependencies import Current_User

api_router = APIRouter(prefix="/webhooks", tags=["Cooperative Admin & Management"])


@api_router.post(
        "/payaza",
        status_code=status.HTTP_200_OK
)
async def payaza_webhook(request: Request):
    return await payaza_service.process_payaza_webhook(request)

