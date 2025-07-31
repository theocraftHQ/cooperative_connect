from fastapi import APIRouter

from theocraft_coop.routers.auth_route import api_router as auth_router

router = APIRouter()

router.include_router(router=auth_router)
