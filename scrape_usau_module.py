import requests
# import urllib.request
# import time
from bs4 import BeautifulSoup

url = 'https://play.usaultimate.org/events/USA-Ultimate-National-Championships-2015/schedule/Men/Club-Men/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
print(soup.prettify())

soup.find_all('h4')
mydivs = soup.findAll("div", {"class": "top_area winner"})