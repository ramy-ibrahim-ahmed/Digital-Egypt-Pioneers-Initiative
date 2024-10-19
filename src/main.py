from fastapi import FastAPI
from .routes import chat, student
from .helpers import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongo_connection = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_connection[settings.MONGODB_DATABASE]
    yield
    app.mongo_connection.close()


app = FastAPI(lifespan=lifespan)

app.include_router(chat.router)
app.include_router(student.router)
