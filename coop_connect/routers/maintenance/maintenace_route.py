from fastapi import APIRouter, Depends, status

from coop_connect.root.permission import CoopSuperAdminOnly, PermissionsDependency
from coop_connect.services.maintenance_service import (
    delete_cooperative,
    delete_non_admin_users,
)

api_router = APIRouter(prefix="/v1/maintenace", tags=["Maintenance Route"])


@api_router.post(
    "/clear-cooperative-db",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionsDependency([CoopSuperAdminOnly]))],
)
async def clear_cooperatives():
    await delete_cooperative()
    return


@api_router.post(
    "/clear-user-db",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionsDependency([CoopSuperAdminOnly]))],
)
async def clear_users():
    await delete_non_admin_users()
    return
