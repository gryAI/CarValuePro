import os
from collections import defaultdict
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from utils.utils import (
    get_logger,
    initialize_web_browser,
    initialize_web_driver,
    sort_listings,
)

log_file = get_logger(
    "FullLoadPipeline - Extract - FO", "logs/applog.log", output_to_console=False
)
log_console = get_logger("FullLoadPipeline - Extract - CO", output_to_file=False)
log_file_console = get_logger("FullLoadPipeline - Extract - FC", "logs/applog.log")


load_dotenv()


def extract(entrypoint):
    """
    Main function to scrape data from the website and save it in the staging folder: data/raw_data
    """
    log_file_console.info("Initializing website .....")
    driver, page_url = initialize_website()
    log_file_console.info("Website initialized .....")

    car_data = initialize_df()

    page = 0
    car_posting = 0

    while True:
        page += 1
        page_soup = get_page_soup(page_url)

        # Exit point for the while loop
        if page_soup.find(class_="box-no-results-search-v2"):
            log_file_console.info(f"Successfully scraped {car_posting} car postings.")
            log_file_console.info(f"No more results found after page {page}.")
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

                listing_info.update(additional_info)
                new_data = pd.DataFrame([listing_info], columns=car_data.columns)
                car_data = pd.concat([car_data, new_data], ignore_index=True)
                car_posting += 1
                log_console.info(
                    f"Page: {page} | Listing no: {car_posting} | Scraped info from: {listing_info['listing_url']}"
                )
                break

            break
        break

    time_stamp = str(datetime.now().date())
    file_path = f"data/raw_data/initial_load_raw_data-{time_stamp}.csv"
    save_data(car_data, file_path)
    log_file_console.info(f"Saved data in {file_path}")
    log_file_console.info("Completed Successfully: Extraction Process")


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
            "price_and_payment_terms": [],
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


def extract_price_and_payment_terms(soup):
    """
    Extracts price and payment term below the photo of the listing on the detail page.
    """

    list_pay_price = soup.find(class_="list-pay-price")
    return (
        {
            li.find("label").text: li.find("span").text
            for li in list_pay_price.find_all("li")
        }
        if list_pay_price
        else {}
    )


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
        "price_and_payment_terms": extract_price_and_payment_terms(soup),
        "negotiation_and_test_drive": [
            span.text.replace("\n", " ").replace("", "").strip()
            for span in soup.find(class_="list-description").find("p")
        ],
        "additional_services": [
            service.text.strip()
            for service in soup.find(class_="box-accompanied-service").find_all(
                class_="text"
            )
        ],
        "complete_listing_description": safe_find(
            soup, "description-content product_detail_des"
        ).strip(),
        "detail_price": get_safe_value("price", 0),
    }


def save_data(car_data, file_path):
    car_data.to_csv(file_path, index=False, encoding="utf-8")


if __name__ == "__main__":
    print("|==============================|")
    print("|         full pipeline        |")
    print("|              |               |")
    print("|         extract.py           |")
    print("|==============================|")
