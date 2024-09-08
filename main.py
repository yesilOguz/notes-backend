from contextlib import asynccontextmanager
from sys import prefix

from fastapi import FastAPI, status, APIRouter

from db_utilities import create_system_admins
from notes_backend.core.mongo_database import MONGO

from notes_backend.user.routes import router as user_router
from notes_backend.group.routes import router as group_router
from notes_backend.notes.routes import router as notes_router
from notes_backend.health.routes import router as health_router
from notes_backend.websocket.routes import router as websocket_router
from notes_backend.deeplinking.routes import router as deeplink_router
from notes_backend.rewards.routes import router as reward_router

router = APIRouter()


@router.get('/', status_code=status.HTTP_200_OK, response_model=dict)
def main():
    return {'nnotes': '0.1.2b'}


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MONGO.check_connection():
        MONGO.reconnect()

    app.database = MONGO.get_db()
    yield
    MONGO.shutdown_db()

create_system_admins()

app = FastAPI(lifespan=lifespan, docs_url=None)

app.include_router(router)
app.include_router(user_router, prefix='/user')
app.include_router(group_router, prefix='/group')
app.include_router(notes_router, prefix='/note')
app.include_router(health_router, prefix='/health')
app.include_router(websocket_router, prefix='/websocket')
app.include_router(reward_router, prefix='/rewards')
app.include_router(deeplink_router, prefix='/.well-known')
