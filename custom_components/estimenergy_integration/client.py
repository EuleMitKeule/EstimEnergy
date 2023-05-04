import requests


class EstimEnergyClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_device(self, name: str):
        url = f"http://{self.host}:{self.port}/api/device/{name}"
        response = requests.get(url, timeout=5)
        return response.json()

    def get_devices(self):
        url = f"http://{self.host}:{self.port}/api/device"
        response = requests.get(url, timeout=5)
        return response.json()

    def get_metrics(self):
        url = f"http://{self.host}:{self.port}/metrics"
        response = requests.get(url, timeout=5)
        return response.text
