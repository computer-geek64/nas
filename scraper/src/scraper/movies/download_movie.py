# download_movie.py
import logging
import asyncio
import aiohttp
import aiofiles
import redis.asyncio as redis
from .source_url_scrapers.fmovies import get_movie_source_url


logger = logging.getLogger(__name__)

redis_client = redis.Redis(host='redis')


async def download_movie_source(movie_name: str, filename: str) -> None:
    movie_source_url, headers = await get_movie_source_url(movie_name)
    logger.debug('Found movie source URL')

    async with aiofiles.open(filename, 'wb') as movie_source_file:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as aiohttp_client:
            start_byte = 0
            while True:
                try:
                    async with aiohttp_client.get(movie_source_url, headers=headers) as response:
                        async for chunk in response.content.iter_chunked(1024):
                            await movie_source_file.write(chunk)
                            start_byte += len(chunk)
                    break
                except asyncio.exceptions.TimeoutError:
                    logger.warning('Timeout occurred, restarting download')
                    headers['Range'] = f'bytes={start_byte}-'

    logger.debug('Finished downloading movie source')
