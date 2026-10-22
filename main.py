import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from handlers.router import router
from consumers.consumer import run


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = threading.Event()
    t = threading.Thread(target=run, args=(stop,), daemon=True)
    t.start()
    try:
        yield
    finally:
        stop.set()
        t.join(timeout=1)


app = FastAPI(lifespan=lifespan)
app.include_router(router)