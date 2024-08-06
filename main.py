from contextlib import asynccontextmanager

from fastapi import FastAPI, status, APIRouter
from notes_backend.core.mongo_database import MONGO

from notes_backend.user.routes import router as user_router
from notes_backend.group.routes import router as group_router

router = APIRouter()


@router.get('/', status_code=status.HTTP_200_OK, response_model=dict)
def main():
    return {'notes': '?'}


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MONGO.check_connection():
        MONGO.reconnect()

    app.database = MONGO.get_db()
    yield
    MONGO.shutdown_db()

app = FastAPI(lifespan=lifespan)

app.include_router(router)
app.include_router(user_router, prefix='/user')
app.include_router(group_router, prefix='/group')

