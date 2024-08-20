# Import Libraries
import time
from collections import defaultdict

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


# Specify the path to the chromedriver executable
chromedriver_path = r"C:\Drivers\chromedriver.exe"


# Set Chrome options
chrome_options = Options()


# Initialize the WebDriver
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)


# Get the url of interest
driver.get("https://philkotse.com/used-cars-for-sale")


# Sort by date posted
sort_recent = driver.find_element(
    By.CSS_SELECTOR, "#order-listing > li:nth-child(3) > a"
)
sort_recent.click()

# Initialize DataFrame
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
        "detail_price": [],
        "additional_price_details": [],
        "additional_services": [],
        "additional_details": [],
        "complete_listing_description": [],
    }
)

page = 0
car_posting = 0
while True:
    page += 1
    page_content = requests.get(
        f"https://philkotse.com/used-cars-for-sale/p{page}"
    ).content
    soup = BeautifulSoup(page_content, "html.parser")

    if soup.find(class_="box-no-results-search-v2"):
        break

    print(f"Page: {page}")

    postings = soup.find_all("div", class_="col-4")

    for car in postings:
        # Car Primary Details
        id = car.get("id")
        dealer_id = car.get("data-dealerid")
        listing_title = car.find(class_="title").text

        try:
            listing_price = car.find(class_="price-repossessed").text
        except:
            listing_price = ""

        listing_location = car.find(class_="location").text

        try:
            url = str(car.find("a").get("href"))
        except:
            continue

        # print(page, url)

        # Parse URL Contents
        car_content = requests.get(f"https://philkotse.com/{url}").content
        car_content_soup = BeautifulSoup(car_content, "html.parser")

        # Car Additional Details
        dtl_date_posted = car_content_soup.find(class_="date-post").text

        try:
            accompanied_service = car_content_soup.find(
                class_="box-accompanied-service"
            )
            accompanied_service_texts = accompanied_service.find_all(class_="text")
            accompanied_service_list = []
            for service in accompanied_service_texts:
                accompanied_service_list.append(service.text)
        except:
            accompanied_service_list = []

        parameter_info = car_content_soup.find(class_="parameter-info")
        parameter_info_list = parameter_info.find(class_="list")
        parameter_info_list_li = parameter_info_list.find_all("li")

        print(url)
        details_dict = defaultdict(list)

        # Map icon class to text
        for li in parameter_info_list_li:
            icon = li.find("i")
            if icon:
                # Use the class names as key
                icon_classes = " ".join(icon.get("class", []))
                # Extract the text after the icon
                text = (
                    li.get_text(strip=True)
                    .replace(icon.get_text(strip=True), "")
                    .strip()
                )
                # Append text to the list associated with the class key
                details_dict[icon_classes].append(text)

        # Convert defaultdict to regular dict for display
        details_dict = dict(details_dict)

        try:
            detail_make = details_dict["icon car"][0]
        except:
            detail_make = ""
        try:
            detail_model = details_dict["icon car"][1]
        except:
            detail_model = ""
        try:
            detail_year = details_dict["icon icon-calendar"][0]
        except:
            detail_year = ""
        try:
            detail_status = details_dict["icon car"][2]
        except:
            detail_status = ""
        try:
            detail_color = details_dict["icon color_car"][0]
        except:
            detail_color = ""
        try:
            detail_transmission = details_dict["icon Transmission"][0]
        except:
            detail_transmission = ""
        try:
            detail_mileage = details_dict["icon icon-gauge"][0]
        except:
            detail_mileage = ""
        try:
            detail_coding = details_dict["icon icon-placenumber"][0]
        except:
            detail_coding = ""

        detail_price = parameter_info.find(class_="price").text

        list_pay_price = car_content_soup.find(class_="list-pay-price")
        list_pay_price_li = list_pay_price.find_all("li")
        list_pay_price_dict = {}
        for li in list_pay_price_li:
            list_pay_price_dict[li.find("label").text] = li.find("span").text

        list_description = car_content_soup.find(class_="list-description")

        list_description_p = list_description.find("p")
        additional_details = []
        for span in list_description_p:
            if span.text.strip(" ") != "":
                additional_details.append(span.text.strip(" "))

        list_description_ul = list_description.find("ul")

        try:
            list_description_ul_li = list_description_ul.find_all("li")
            additional_features = []
            for li in list_description_ul_li:
                additional_features.append(li.text)
        except:
            additional_features = []

        complete_description = list_description.find(
            class_="description-content product_detail_des"
        ).text.strip()

        new_data = pd.DataFrame(
            [
                {
                    "listing_id": id,
                    "dealer_id": dealer_id,
                    "listing_title": listing_title,
                    "listing_price": listing_price,
                    "listing_location": listing_location,
                    "listing_url": url,
                    "detail_date_posted": dtl_date_posted,
                    "detail_make": detail_make,
                    "detail_model": detail_model,
                    "detail_year": detail_year,
                    "detail_status": detail_status,
                    "detail_color": detail_color,
                    "detail_transmission": detail_transmission,
                    "detail_mileage": detail_mileage,
                    "detail_coding": detail_coding,
                    "detail_price": detail_price,
                    "detail_features": additional_features,
                    "additional_price_details": list_pay_price_dict,
                    "additional_services": accompanied_service_list,
                    "additional_details": additional_details,
                    "complete_listing_description": complete_description,
                }
            ],
            columns=car_data.columns,
        )

        car_data = pd.concat([car_data, new_data], ignore_index=True)
        car_posting += 1

        print(page, car_posting, detail_price, "Loading complete for ", url)

        time.sleep(0.5)

# Save data to .csv
car_data.to_csv(
    "data/raw_data/initial_load_raw_data.csv", index=False, encoding="utf-8"
)

# Quit the driver
driver.quit()
