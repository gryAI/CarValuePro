import os
import time
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
