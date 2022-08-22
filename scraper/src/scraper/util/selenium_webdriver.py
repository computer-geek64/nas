# selenium_webdriver.py
import logging
from typing import Callable, Any
from functools import wraps
from selenium import webdriver


logger = logging.getLogger(__name__)


def selenium_url_scraper(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs) -> tuple[str, dict[str, str]] | None:
        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options)

        try:
            url, headers = await func(*args, **kwargs, driver=driver)
        except Exception as e:
            logger.exception(e)
            driver.quit()
            return None

        headers['User-Agent'] = driver.execute_script('return navigator.userAgent;')

        driver.quit()
        return url, headers

    return wrapper
