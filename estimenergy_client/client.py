
import requests


class EstimEnergyClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_data(self, name):
        url = f"http://{self.host}:{self.port}/collector/{name}/data"
        response = requests.get(url)
        return response.json()
    
    async def async_get_data(self, name):
        url = f"http://{self.host}:{self.port}/collector/{name}/data"
        response = await requests.get(url)
        return response.json()