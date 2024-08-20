import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def initialize_web_driver(path):
    chromedriver_path = path
    chrome_options = Options()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def initialize_web_browser(driver, url):
    driver.get(url)

    return driver


def sort_listings(driver):
    sort_recent = driver.find_element(
        By.CSS_SELECTOR, "#order-listing > li:nth-child(3) > a"
    )

    sort_recent.click()


def get_logger(
    name: str,
    log_file: str = None,
    level=logging.DEBUG,
    output_to_console=True,
    output_to_file=True,
) -> logging.Logger:
    """
    Set up a logger that logs to console, file, or both.

    :param name: The name of the logger.
    :param log_file: The path to the log file. If None, no file logging is used.
    :param level: The logging level.
    :param output_to_console: Whether to log to console.
    :param output_to_file: Whether to log to file.
    :return: A configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if not logger.hasHandlers():
        # Create formatters
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Optionally add a file handler
        if output_to_file and log_file:
            # Ensure the log directory exists
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Optionally add a console handler
        if output_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger
