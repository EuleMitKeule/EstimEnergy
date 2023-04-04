import requests


class EstimEnergyClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_collector(self, id):
        url = f"http://{self.host}:{self.port}/collector/{id}"
        response = requests.get(url, timeout=5)
        return response.json()

    async def async_get_collector(self, id):
        url = f"http://{self.host}:{self.port}/collector/{id}"
        response = await requests.get(url, timeout=5)
        return response.json()

    def get_collectors(self):
        url = f"http://{self.host}:{self.port}/collector"
        response = requests.get(url, timeout=5)
        return response.json()

    async def async_get_collectors(self):
        url = f"http://{self.host}:{self.port}/collector"
        response = await requests.get(url, timeout=5)
        return response.json()

    def get_metrics(self):
        url = f"http://{self.host}:{self.port}/metrics"
        response = requests.get(url, timeout=5)
        return response.text
