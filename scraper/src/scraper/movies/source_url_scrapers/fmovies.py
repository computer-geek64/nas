# fmovies.py
import logging
import asyncio
from ...util.selenium_webdriver import selenium_url_scraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import JavascriptException


logger = logging.getLogger(__name__)


@selenium_url_scraper
async def get_movie_source_url(movie_name: str, *args, **kwargs) -> tuple[str, dict[str, str]] | None:
    """
    Retrieve video source URL for movie

    Searches fmoviesto.cc by movie name for mp4 source URL
    """

    driver: WebDriver = kwargs['driver']
    headers = {}

    driver.get('https://fmoviesto.cc')

    await asyncio.sleep(3)

    search_bar = driver.find_element(By.CSS_SELECTOR, 'input.search-input')
    search_bar.send_keys(movie_name)

    await asyncio.sleep(1)

    search_bar.send_keys(Keys.ENTER)

    await asyncio.sleep(3)

    search_results = driver.find_elements(By.CSS_SELECTOR, 'a.film-poster-ahref')
    if not search_results:
        logger.error(f'No such movie found: {movie_name}')
        raise ValueError(f'No such movie found: {movie_name}')

    movie_page = search_results[0].get_attribute('href')
    driver.get(movie_page)

    await asyncio.sleep(3)

    server_url = driver.find_elements(By.CSS_SELECTOR, 'a[id^=\"watch-\"]')[0].get_attribute('href')
    driver.get(server_url)

    await asyncio.sleep(5)

    driver.switch_to.frame(0)
    while True:
        try:
            driver.execute_script('document.querySelector(\'div[button=\"download-button\"]\').click();')
            break
        except JavascriptException:
            logger.warning('Could not find download button for video, retrying in 5s...')
            driver.switch_to.default_content()
            driver.refresh()
            await asyncio.sleep(5)
            driver.switch_to.frame(0)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    await asyncio.sleep(5)

    assert driver.current_url.startswith('https://ninjashare.to/')
    driver.get(driver.find_element(By.CSS_SELECTOR, 'div.dls-download > a[href^=\"https://streamlare.com/\"]').get_attribute('href'))

    await asyncio.sleep(3)

    movie_source_url = driver.find_elements(By.CSS_SELECTOR, 'div#downloadCollapse > div.card-body > a[download]')[0].get_attribute('href')
    return movie_source_url, headers
