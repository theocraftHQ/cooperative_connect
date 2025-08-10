import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from theocraft_coop.root.api_router import router

LOGGER = logging.getLogger(__name__)


def intialize() -> FastAPI:
    app = FastAPI()
    app.include_router(router=router)

    return app


app = intialize()


@app.get("/", status_code=307)
def root():
    return RedirectResponse(url="/docs")
