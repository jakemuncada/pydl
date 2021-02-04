import os
import requests
from bs4 import BeautifulSoup

os.environ['NO_PROXY'] = '127.0.0.1'
page = requests.get("http://127.0.0.1:3000/pages/main.html")
soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())
