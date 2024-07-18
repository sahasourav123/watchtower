import os
import requests

PERFORMANCE_SERVICE = os.getenv('BACKEND_SERVICE', 'http://backend:8000/api/v1')

def load_service():
    print(f"Loading Data: performance-service")
    res = requests.get(PERFORMANCE_SERVICE)
    return res.json()
