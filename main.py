from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from database import Base, engine
from routers import router


TITLE_APP = 'Essence API'
DESC_APP = 'CRUD API на FastAPI + SQLAlchemy'
APP_VERSION = '1.0'


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=TITLE_APP,
    description=DESC_APP,
    version=APP_VERSION,
    lifespan=lifespan,
)


app.include_router(router)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
