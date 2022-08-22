# download_trailer.py
import logging
import asyncio
import aiohttp
import aiofiles
from selenium import webdriver
from selenium.webdriver.common.by import By


logger = logging.getLogger(__name__)


async def get_movie_trailer_source_url(imdb_id: str) -> str:
    options = webdriver.FirefoxOptions()
    options.headless = True

    driver = webdriver.Firefox(options=options)
    driver.get(f'https://www.imdb.com/title/{imdb_id}/videogallery/content_type-trailer/')

    await asyncio.sleep(3)

    trailer_url = driver.find_element(By.CSS_SELECTOR, 'h2 > a.video-modal').get_attribute('href')
    driver.get(trailer_url)

    await asyncio.sleep(3)

    driver.execute_script('document.querySelector(\'video.jw-video\').click();')

    await asyncio.sleep(3)

    driver.execute_script('video = document.querySelector(\'video.jw-video\'); video.currentTime = video.duration;')

    await asyncio.sleep(3)

    trailer_source_url = driver.find_element(By.CSS_SELECTOR, 'div.jw-media > video.jw-video').get_attribute('src')
    return trailer_source_url


async def download_movie_trailer_source(imdb_id: str, filename: str) -> None:
    movie_trailer_source_url = await get_movie_trailer_source_url(imdb_id)
    logger.debug('Found movie trailer source URL')

    async with aiohttp.ClientSession() as aiohttp_client:
        async with aiohttp_client.get(movie_trailer_source_url) as response:
            async with aiofiles.open(filename, 'wb') as movie_trailer_source_file:
                async for chunk in response.content.iter_chunked(1000000):
                    await movie_trailer_source_file.write(chunk)

    logger.debug('Finished downloading movie trailer')
