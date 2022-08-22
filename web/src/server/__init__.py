# __init__.py
from . import music
from . import videos
from .util.logger import init_logger
from fastapi import FastAPI, responses


logger = init_logger(__name__)

app = FastAPI()
app.include_router(videos.app)
app.include_router(music.app)


@app.get('/', response_class=responses.PlainTextResponse)
async def get_home():
    return 'Welcome to NAS!'


logger.info('Created FastAPI app and registered API routers')
