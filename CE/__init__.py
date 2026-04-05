import time
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from CE.connections.redis import init_redis
from .property.routes import property_router
from .location.routes import location_router
from .floor.routes import floor_router
from .room.routes import room_router
from .device.routes import device_router
from .connections.sqlite import init_core_db, init_pc_db
from .connections.mqtt import init_mqtt
from .default_insertion import init_default_data

version = 'v1'

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    await init_core_db()
    await init_pc_db()
    await init_default_data()
    await init_mqtt()
    print("Starting up...")
    yield
    print("Shutting down...")

app = FastAPI(
    version=version,
    title="EdgeProcessor",
    description="A microservice for processing edge data.",
    lifespan=lifespan
)

app.include_router(property_router, prefix=f"/api/{version}/property", tags=["Property"])
app.include_router(location_router, prefix=f"/api/{version}/location", tags=["Location"])
app.include_router(floor_router, prefix=f"/api/{version}/floor", tags=["Floor"])
app.include_router(room_router, prefix=f"/api/{version}/room", tags=["Room"])
app.include_router(device_router, prefix=f"/api/{version}/device", tags=["Device"])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}"

    print(f"{request.method} {request.url.path} took {duration:.4f}s")

    return response

@app.get("/")
async def read_root() -> dict:
    return {"msg": "Hello World"}