# __init__.py
from . import movies, shows
from fastapi import APIRouter, responses


app = APIRouter(prefix='/videos', tags=['videos'])
app.include_router(movies.app)
app.include_router(shows.app)


@app.get('/', response_class=responses.PlainTextResponse)
async def get_videos():
    return 'Welcome to videos!'
