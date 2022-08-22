# movies.py
import os
import re
import json
import logging
import asyncio
import aiohttp
import urllib.parse
import redis.asyncio as redis
from ..config import config
from typing import Optional, Generator
from fastapi import APIRouter, responses, HTTPException, Path, Query, Body


logger = logging.getLogger(__name__)

app = APIRouter(prefix='/movies', tags=['movies'])

redis_client = redis.Redis(host='redis')


async def tmdb_movie_search(query: str, page: int = 1) -> list[dict, ...]:
    """
    Search for movies in TMDB

    Searches The Movie Database for movies with names that match the search query
    """

    async with aiohttp.ClientSession() as aiohttp_client:
        tmdb_api_movie_search_parameters = {
            'api_key': os.environ['TMDB_API_KEY'],
            'language': 'en-US',
            'page': page,
            'include_adult': False,
            'query': query
        }

        tmdb_api_movie_search_encoded_query = '&'.join(key + '=' + urllib.parse.quote(str(value), safe='') for key, value in tmdb_api_movie_search_parameters.items())

        async with aiohttp_client.get(config['TMDB']['API_URL'] + f'search/movie?{tmdb_api_movie_search_encoded_query}') as response:
            try:
                assert response.status == 200
            except AssertionError:
                logger.error(f'TMDB API returned a status code of {response.status}')
                return []

            search_results = await response.json()

    return search_results['results']


async def save_movie_metadata(tmdb_id: int) -> Optional[str]:
    """
    Adds movies metadata to library

    Saves movies metadata information to Redis based on The Movie Database ID
    """

    async with aiohttp.ClientSession() as aiohttp_client:
        tmdb_api_get_movie_parameters = {
            'api_key': os.environ['TMDB_API_KEY'],
            'language': 'en-US'
        }

        tmdb_api_get_movie_encoded_query = '&'.join(key + '=' + urllib.parse.quote(str(value), safe='') for key, value in tmdb_api_get_movie_parameters.items())

        async with aiohttp_client.get(config['TMDB']['API_URL'] + f'movie/{tmdb_id}?{tmdb_api_get_movie_encoded_query}') as response:
            try:
                assert response.status == 200
            except AssertionError:
                logger.error(f'Failed to retrieve movies metadata, TMDB API returned a status code of {response.status}')
                return None

            movie = await response.json()

        movie_id = movie['imdb_id']
        movie_name = movie['title']

        async with aiohttp_client.get(config['TMDB']['IMAGE_URL'] + config['TMDB']['IMAGE_QUALITY'] + movie['poster_path']) as response:
            try:
                assert response.status == 200
            except AssertionError:
                logger.error(f'Failed to retrieve movies poster, TMDB returned a status code of {response.status}')
                return None

            movie_poster = await response.read()

        async with aiohttp_client.get(config['TMDB']['IMAGE_URL'] + config['TMDB']['IMAGE_QUALITY'] + movie['backdrop_path']) as response:
            try:
                assert response.status == 200
            except AssertionError:
                logger.error(f'Failed to retrieve movies backdrop, TMDB returned a status code of {response.status}')
                return None

            movie_backdrop = await response.read()

    movie_metadata = {
        'tmdb_id': movie['id'],
        'title': movie_name,
        'description': movie['overview'],
        'tagline': movie['tagline'],
        'date': movie['release_date'],
        'duration': movie['runtime'],
        'language': movie['original_language'],
        'genres': json.dumps({genre['id']: genre['name'] for genre in movie['genres']}),
        'rating': movie['vote_average'],
        'ratings': movie['vote_count'],
        'status': movie['status'],
        'collection_id': movie['belongs_to_collection']['id'] if movie['belongs_to_collection'] else '',
        'collection_name': movie['belongs_to_collection']['name'] if movie['belongs_to_collection'] else '',
        'poster': movie_poster,
        'poster_extension': os.path.splitext(movie['poster_path'])[1],
        'backdrop': movie_backdrop,
        'backdrop_extension': os.path.splitext(movie['backdrop_path'])[1]
    }

    for key, value in movie_metadata.items():
        await redis_client.hset(movie_id, key, value)

    logger.debug(f'Added "{movie_name}" movie metadata to Redis')

    return movie_id


async def save_movie_trailer(movie_id: str) -> str:
    movie_directory = (await redis_client.hget(movie_id, 'directory')).decode()
    trailer_source_filename = os.path.join(movie_directory, 'trailer.mp4')

    job_payload = {
        'job': 'download_movie_trailer_source',
        'args': {
            'filename': trailer_source_filename,
            'imdb_id': movie_id
        }
    }

    await redis_client.publish('scraper_jobs', json.dumps(job_payload))

    return trailer_source_filename


async def save_movie_subtitles(movie_id: str) -> str:
    # TODO: add loop for each subtitle extension
    movie_directory = (await redis_client.hget(movie_id, 'directory')).decode()
    subtitle_sources = ()
    subtitle_source_filenames = []
    return ''


async def save_movie_source(movie_id: str) -> str:
    movie_name = (await redis_client.hget(movie_id, 'title')).decode()
    movie_directory = (await redis_client.hget(movie_id, 'directory')).decode()
    movie_source_filename = os.path.join(movie_directory, 'movie.mp4')

    job_payload = {
        'job': 'download_movie_source',
        'args': {
            'movie_name': movie_name,
            'filename': movie_source_filename
        }
    }

    await redis_client.publish('scraper_jobs', json.dumps(job_payload))

    return movie_source_filename


async def scan_movies_filesystem(path: str) -> Generator[int, None, None]:
    """
    Scans filesystem for movies

    Indexes the provided filepath for any movies and subtitles, yielding movies as they are found
    """
    # TODO: Prepend movie_id key in Redis with movie_
    # TODO: Force copying of existing movies to uniform source?

    path = os.path.abspath(path)

    video_extensions = {'.mp4'}
    subtitle_extensions = {'.vtt', '.srt'}

    if not os.path.exists(path):
        logger.error(f'{path} does not exist')
        raise HTTPException(404, 'Path not found')

    logger.info(f'Scanning {path} in filesystem for movies')

    for root, directories, filenames in os.walk(path):
        movie_source = None
        trailer_source = None
        subtitle_sources = {}
        for filename in filenames:
            extension = os.path.splitext(filename)[1]

            if extension in video_extensions:
                if os.path.splitext(filename)[0] == os.path.basename(root).strip('/'):
                    movie_source = os.path.join(root, filename)
                elif 'trailer' in filename.lower():
                    trailer_source = os.path.join(root, filename)
                elif movie_source is None:
                    movie_source = os.path.join(root, filename)
            elif extension in subtitle_extensions and extension not in subtitle_sources:
                subtitle_sources[extension] = filename

        if movie_source is not None:
            movie_name = os.path.basename(root).strip('/')
            search_results = await tmdb_movie_search(movie_name)

            if not search_results:
                logger.warning(f'Movie search results not found for "{movie_name}"')
                continue

            tmdb_id = search_results[0]['id']
            yield tmdb_id, movie_source, trailer_source, subtitle_sources


@app.get('/', response_class=responses.JSONResponse)
async def get_movies():
    """
    Get a listing of all available movies

    GET /movies
    """

    return await redis_client.keys()


@app.post('/add', response_class=responses.PlainTextResponse)
async def add_movie(name: str = Body(title='Name', description='Name of movies', embed=True)):
    """
    Add movies by name to the library

    POST /movies/add
    """
    # movie_source_filename = os.path.join(movie_directory, re.sub('[^a-zA-Z0-9 .,:\'\\-!?&$_+()]+', '', movie_name))

    search_results = await tmdb_movie_search(name)
    if not search_results:
        logger.warning(f'Movie search results not found for "{name}"2')
        raise HTTPException(404, f'Movie search results not found for "{name}"')

    tmdb_id = search_results[0]['id']
    movie_name = search_results[0]['title']
    movie_id = await save_movie_metadata(tmdb_id)

    movie_directory = os.path.join(os.path.abspath(config['MOVIES']['NEW']['BASE_PATH']), re.sub('[^a-zA-Z0-9 .,:\'\\-!?&$_+()]+', '', movie_name))
    os.makedirs(movie_directory)
    await redis_client.hset(movie_id, 'directory', movie_directory)

    # Download trailer
    trailer_source = await save_movie_trailer(movie_id)
    await redis_client.hset(movie_id, 'trailer', trailer_source)

    # Download subtitles
    # subtitle_sources = await save_movie_subtitles(movie_id)
    # await redis_client.hset(movie_id, 'subtitles', '')  # TODO: fix this

    # Download source
    movie_source = await save_movie_source(movie_id)
    await redis_client.hset(movie_id, 'source', movie_source)

    return 'Success'


@app.post('/scan', response_class=responses.JSONResponse)
async def scan_movies(path: str = Body(title='Path', description='Directory path of filesystem to be scanned', embed=True)):
    """
    Scan existing movies into library based on path

    POST /movies/scan
    """

    async for tmdb_id, movie_source, movie_trailer_source, movie_subtitle_sources in scan_movies_filesystem(path):
        movie_id = await save_movie_metadata(tmdb_id)
        await redis_client.hset(movie_id, 'directory', os.path.dirname(movie_source))
        await redis_client.hset(movie_id, 'source', movie_source)

        if movie_trailer_source is None:
            movie_trailer_source = await save_movie_trailer(movie_id)
        await redis_client.hset(movie_id, 'trailer', movie_trailer_source)

        if movie_subtitle_sources is None:
            movie_subtitle_sources = await save_movie_subtitles(movie_id)
        await redis_client.hset(movie_id, 'subtitles', json.dumps(movie_subtitle_sources))

    return [await save_movie_metadata(tmdb_id) async for tmdb_id in scan_movies_filesystem(path)]


@app.get('/{movie_id}', response_class=responses.JSONResponse)
async def get_movie(movie_id: str = Path(title='Movie ID', description='IMDB ID of movies')):
    return await redis_client.hgetall(movie_id)


@app.put('/{movie_id}', response_class=responses.PlainTextResponse)
async def update_movie(movie_id: str = Path(title='Movie ID', description='IMDB ID of movies')):
    raise NotImplementedError()


@app.delete('/{movie_id}', response_class=responses.PlainTextResponse)
async def delete_movie(movie_id: str = Path(title='Movie ID', description='IMDB ID of movies')):
    if await redis_client.delete(movie_id):
        return 'Success'
    else:
        logger.error(f'Movie with ID {movie_id} could not be deleted')
        raise HTTPException(400, f'Movie with ID {movie_id} could not be deleted')
