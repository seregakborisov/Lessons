import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from handlers.router import router
from consumers.consumer import run


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task = asyncio.create_task(run())

    try:
        yield
    finally:
        consumer_task.cancel()

        try:
            await consumer_task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)

app.include_router(router)