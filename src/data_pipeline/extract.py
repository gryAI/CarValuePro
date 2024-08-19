# Import Libraries
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait





# Configure Selenium Web Driver
driver = webdriver.Chrome("C:\Drivers\chromedriver.exe")
driver.get("https://philkotse.com/used-cars-for-sale")