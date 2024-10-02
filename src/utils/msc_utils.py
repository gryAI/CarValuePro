import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


# Extraction Common Functions
def initialize_web_driver(path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure Chrome runs headless
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument(
        "--disable-dev-shm-usage"
    )  # Overcome limited resource issues
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage for simplicity
    chrome_options.add_argument("--window-size=1920x1080")  # Set screen size
    chrome_options.add_argument(
        "--remote-debugging-port=9222"
    )  # Enable remote debugging
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument(
        "--disable-dev-shm-usage"
    )  # Overcome shared memory issues

    service = Service(ChromeDriverManager().install())
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


# Logging Functions
def get_logger(
    name: str,
    log_file: str = "logs/applog.log",
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

        # Optionally add a console handler
        if output_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger


def customize_logger(feature, subfeature):
    if feature == "extract":
        if subfeature == "incremental":
            # log_file = get_logger("IL_PIPELINE - Extract - FO", output_to_console=False)
            log_console = get_logger("IL_PIPELINE - Extract - CO", output_to_file=False)
            # log_file_console = get_logger("IL_PIPELINE - Extract - FC")

        elif subfeature == "full":
            # log_file = get_logger("FL_PIPELINE - Extract - FO", output_to_console=False)
            log_console = get_logger("FL_PIPELINE - Extract - CO", output_to_file=False)
            # log_file_console = get_logger("FL_PIPELINE - Extract - FC")

    elif feature == "transform":
        if subfeature == "incremental":
            # log_file = get_logger(
            #     "IL_PIPELINE - Transform - FO", output_to_console=False
            # )
            log_console = get_logger(
                "IL_PIPELINE - Transform - CO", output_to_file=False
            )
            # log_file_console = get_logger("IL_PIPELINE - Transform - FC")

        elif subfeature == "full":
            # log_file = get_logger(
            #     "FL_PIPELINE - Transform - FO", output_to_console=False
            # )
            log_console = get_logger(
                "FL_PIPELINE - Transform - CO", output_to_file=False
            )
            # log_file_console = get_logger("FL_PIPELINE - Transform - FC")

    elif feature == "load":
        if subfeature == "incremental":
            # log_file = get_logger("IL_PIPELINE - Load - FO", output_to_console=False)
            log_console = get_logger("IL_PIPELINE - Load - CO", output_to_file=False)
            # log_file_console = get_logger("IL_PIPELINE - Load - FC")

        elif subfeature == "full":
            # log_file = get_logger("FL_PIPELINE - Load - FO", output_to_console=False)
            log_console = get_logger("FL_PIPELINE - Load - CO", output_to_file=False)
            # log_file_console = get_logger("FL_PIPELINE - Load - FC")

    else:
        print("Invalid parameters")

    # return log_file, log_console, log_file_console
    return log_console
