# shows.py
from fastapi import APIRouter, responses


app = APIRouter(tags=['shows'])


@app.get('/shows', response_class=responses.PlainTextResponse)
async def get_shows():
    return 'Welcome to shows!'
