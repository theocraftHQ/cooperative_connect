from fastapi import APIRouter

from theocraft_coop.routers.auth_route import api_router as auth_router
from theocraft_coop.routers.misc_route import api_router as misc_router
from theocraft_coop.routers.cooperative_route import api_router as cooperative_route

router = APIRouter()

router.include_router(router=auth_router)
router.include_router(router=misc_router)
router.include_router(router=cooperative_route)
