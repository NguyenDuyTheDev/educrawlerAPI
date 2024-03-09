import requests
from datetime import datetime

while True:
  current = datetime.now()
  if current.minute % 15 == 0 and current.second == 0:
    requests.get('https://educrawlercrawlerservice.onrender.com')
    requests.get('https://educrawlerapi.onrender.com/docs#/')
    print(current)
