import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from coop_connect.root.api_router import router
from coop_connect.root.coop_enums import Environment
from coop_connect.root.settings import settings

LOGGER = logging.getLogger(__name__)


def intialize() -> FastAPI:
    app = FastAPI()
    app.include_router(router=router)

    return app


app = intialize()


@app.get("/health-check")
def health_check():
    return {"message": "server is up, and healthy"}


@app.get("/", status_code=307)
def root():
    url = "/docs"
    if settings.environment == Environment.PRODUCTION:
        url = "/health-check"
    return RedirectResponse(url=url)
