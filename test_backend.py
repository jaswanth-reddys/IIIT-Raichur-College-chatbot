import requests
import json

url = "http://localhost:8000/ask"
data = {"question": "What is IIITR?"}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
