import requests
import json
from concurrent.futures import ThreadPoolExecutor

def make_api_call():


  url = "http://localhost:8000/error"

  payload = {}
  headers = {}

  response = requests.request("GET", url, headers=headers, data=payload)

  print(response.text)



num_requests = 100

with ThreadPoolExecutor(max_workers=num_requests) as executor:
    futures = [executor.submit(make_api_call) for _ in range(num_requests)]

    for future in futures:
        future.result()