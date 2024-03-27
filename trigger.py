import requests
from datetime import datetime

while True:
  try:
    current = datetime.now()
    if current.minute % 5 == 0 and current.second > 0 and current.second < 3:
      requests.get('https://educrawlercrawlerservice.onrender.com')
      requests.get('https://educrawlerapi.onrender.com/docs#/')
      print(current)
  except:
    print("Err")
