# __init__.py
import json
import asyncio
import redis.asyncio as redis
from .util.logger import init_logger
from .movies.download_trailer import download_movie_trailer_source
from .movies.download_movie import download_movie_source


logger = init_logger(__name__)


async def job_scheduler():
    redis_client = redis.Redis(host='redis')
    redis_pubsub = redis_client.pubsub()
    await redis_pubsub.subscribe('scraper_jobs')

    channels = ', '.join(channel.decode() for channel in redis_pubsub.channels)
    logger.warning(f'Subscribed to channels: {channels}')

    jobs = asyncio.Queue()

    async for message in redis_pubsub.listen():
        if isinstance(message, dict) and message['type'] == 'message':
            if message['channel'].decode() == 'scraper_jobs':
                logger.debug('Job received')
                payload = json.loads(message['data'])
                if payload['job'] == 'download_movie_trailer_source':
                    filename = payload['args']['filename']
                    imdb_id = payload['args']['imdb_id']
                    task = asyncio.create_task(download_movie_trailer_source(imdb_id, filename))
                elif payload['job'] == 'download_movie_source':
                    filename = payload['args']['filename']
                    movie_name = payload['args']['movie_name']
                    task = asyncio.create_task(download_movie_source(movie_name, filename))

    await redis_pubsub.unsubscribe()
    await redis_client.close()
