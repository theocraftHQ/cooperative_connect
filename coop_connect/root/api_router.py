from fastapi import APIRouter

from coop_connect.routers.auth_route import api_router as auth_router
from coop_connect.routers.misc_route import api_router as misc_router
from coop_connect.routers.auth_route import api_router as coop_auth_router
from coop_connect.routers.coop_member_route import api_router as coop_member_router
from coop_connect.routers.coop_route import api_router as coop_router

router = APIRouter()

router.include_router(router=auth_router)
router.include_router(router=misc_router)
router.include_router(router=coop_auth_router)
router.include_router(router=coop_router)
router.include_router(router=coop_member_router)
