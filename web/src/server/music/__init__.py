# __init__.py
from fastapi import APIRouter, responses


app = APIRouter(prefix='/music', tags=['music'])


@app.get('/', response_class=responses.PlainTextResponse)
async def get_home():
    return 'Welcome to music!'
