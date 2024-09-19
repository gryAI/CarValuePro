import os
import time
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from utils.msc_utils import (
    customize_logger,
    initialize_web_browser,
    initialize_web_driver,
    sort_listings,
)

load_dotenv()


def extract(entrypoint, is_incremental, to_skip = 0):
    """
    Scrapes data from the website and saves it in the staging folder: data/raw_data.

    Args:
        entrypoint (str): The URL of the website to scrape.
        is_incremental (bool): Specifies whether the pipeline is full or incremental.
        to_skip (int): Applicable only for the incremental pipeline. This variable allows
            the scraper to skip a specified number of postings that do not match yesterday's
            date. This is necessary because the website's sorting by recent postings may not
            work correctly, and this ensures that all postings from yesterday are checked.
    """

    if is_incremental:
        log_console = customize_logger(
            feature="extract", subfeature="incremental"
        )
    else:
        log_console = customize_logger(
            feature="extract", subfeature="full"
        )

    log_console.info("Initializing website .....")
    driver, page_url = initialize_website()
    log_console.info("Website initialized .....")

    car_data = initialize_df()

    page = 0
    car_posting = 0
    skipped_postings = 0
    while True:
        page += 1
        page_soup = get_page_soup(f"{page_url}/p{page}")

        # Exit point 2 for the while loop in full pipeline
        if page_soup.find(class_="box-no-results-search-v2"):
            log_console.info(f"Successfully scraped {car_posting} car postings.")
            log_console.info(f"No more results found after page {page}.")
            break

        # Exit point for the while loop in incremental pipeline
        if skipped_postings >= to_skip:
            log_console.info(f"Successfully scraped {car_posting} car postings.")
            break

        # Entry point for scraping
        else:
            log_console.info(f"Scraping Page: {page}")
            postings = page_soup.find_all("div", class_="col-4")

            # Scrape listing info on the summary page
            for car in postings:
                listing_info = extract_listing_info(car)
                if not listing_info["listing_url"]:
                    continue

                # Scrape additional info based on the listing url
                car_details_soup = get_page_soup(
                    f"{entrypoint}{listing_info['listing_url']}"
                )
                additional_info = extract_additional_details(car_details_soup)

                # Condition for incremental pipeline
                if is_incremental:
                    if is_posted_yesterday(additional_info["detail_date_posted"]):
                        pass
                    else:
                        skipped_postings += 1
                        continue

                listing_info.update(additional_info)
                new_data = pd.DataFrame([listing_info], columns=car_data.columns)
                car_data = pd.concat([car_data, new_data], ignore_index=True)
                car_posting += 1
                log_console.info(
                    f"Page: {page} | Listing no: {car_posting} | Scraped info from: {listing_info['listing_url']}"
                )

                time.sleep(0.5)

            # Exit point 1 for the while loop in full pipeline
            if listing_info["listing_title"] == "":
                log_console.info(
                    f"Successfully scraped {car_posting} car postings."
                )
                log_console.info(f"No more results found after page {page}.")
                break

    log_console.info("Exiting: Extraction process completed successfully!")

    return car_data


def initialize_website():
    driver_path = os.getenv("CHROMEDRIVER_PATH")
    page_url = os.getenv("CHROMEBROWSER_URL")
    driver = initialize_web_driver(driver_path)
    driver = initialize_web_browser(driver, page_url)
    sort_listings(driver)

    return driver, page_url


def initialize_df():
    car_data = pd.DataFrame(
        {
            "listing_id": [],
            "dealer_id": [],
            "listing_title": [],
            "listing_price": [],
            "listing_location": [],
            "listing_url": [],
            "detail_date_posted": [],
            "detail_make": [],
            "detail_model": [],
            "detail_year": [],
            "detail_status": [],
            "detail_color": [],
            "detail_transmission": [],
            "detail_mileage": [],
            "detail_coding": [],
            "detail_features": [],
            "negotiation_and_test_drive": [],
            "additional_services": [],
            "complete_listing_description": [],
            "detail_price": [],
        }
    )

    return car_data


def get_page_soup(url):
    page_soup = requests.get(url).content
    return BeautifulSoup(page_soup, "html.parser")


def safe_find(soup, class_name, default=""):
    element = soup.find(class_=class_name)
    return element.text if element else default


def is_posted_yesterday(date_string):
    date_string = date_string.replace("Posted on ", "")
    date_obj = datetime.strptime(date_string, "%d/%m/%Y").date()

    now = datetime.now().date()
    yesterday = now - timedelta(days=1)

    return date_obj == yesterday


def extract_listing_info(soup):
    """
    Extracts car details from the summary listing page.
    """

    return {
        "listing_id": soup.get("id"),
        "dealer_id": soup.get("data-dealerid"),
        "listing_title": safe_find(soup, "title"),
        "listing_price": safe_find(soup, "price-repossessed"),
        "listing_location": safe_find(soup, "location"),
        "listing_url": soup.find("a").get("href") if soup.find("a") else None,
    }


def get_details_dict(soup):
    """
    Gets additional car details on the right pane of the details page.
    """

    details_dict = defaultdict(list)
    parameter_info = soup.find(class_="parameter-info")
    parameter_info_list = parameter_info.find(class_="list")
    if parameter_info_list:
        for li in parameter_info_list.find_all("li"):
            icon = li.find("i")
            if icon:
                icon_classes = " ".join(icon.get("class", []))
                text = (
                    li.get_text(strip=True)
                    .replace(icon.get_text(strip=True), "")
                    .strip()
                )
                details_dict[icon_classes].append(text)

    details_dict["price"].append(safe_find(parameter_info, "price"))
    return dict(details_dict)


def extract_additional_details(soup):
    """
    Extracts additional details from the details page based on details_dict and the details page soup.
    """

    details_dict = get_details_dict(soup)

    def get_safe_value(dict_key, index, default=""):
        """
        Safely retrieves a value from details_dict, returning a default if the index is out of range.
        """
        try:
            return details_dict.get(dict_key, [default])[index]
        except IndexError:
            return default

    detail_features_element = soup.find(class_="list-description").find("ul")
    detail_features = (
        [features.text for features in detail_features_element.find_all("li")]
        if detail_features_element
        else []
    )

    negotiation_and_test_drive_element = soup.find(class_="list-description")
    negotiation_and_test_drive = (
        [
            span.text.replace("\n", " ").replace("", "").strip()
            for span in negotiation_and_test_drive_element.find("p")
        ]
        if negotiation_and_test_drive_element
        else []
    )

    additional_services_element = soup.find(class_="box-accompanied-service")
    additional_services = (
        [
            service.text.strip()
            for service in additional_services_element.find_all(class_="text")
        ]
        if additional_services_element
        else []
    )

    return {
        "detail_date_posted": safe_find(soup, "date-post"),
        "detail_make": get_safe_value("icon car", 0),
        "detail_model": get_safe_value("icon car", 1),
        "detail_year": get_safe_value("icon icon-calendar", 0),
        "detail_status": get_safe_value("icon car", 2),
        "detail_color": get_safe_value("icon color_car", 0),
        "detail_transmission": get_safe_value("icon Transmission", 0),
        "detail_mileage": get_safe_value("icon icon-gauge", 0),
        "detail_coding": get_safe_value("icon icon-placenumber", 0),
        "detail_features": detail_features,
        "negotiation_and_test_drive": negotiation_and_test_drive,
        "additional_services": additional_services,
        "complete_listing_description": safe_find(
            soup, "description-content product_detail_des"
        ).strip(),
        "detail_price": get_safe_value("price", 0),
    }


if __name__ == "__main__":
    print("|==============================|")
    print("|           pipeline           |")
    print("|              |               |")
    print("|          extract.py          |")
    print("|==============================|")
