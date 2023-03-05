
from prometheus_client.registry import Collector as Metrics
from estimenergy.const import METRICS

from estimenergy.models.collector_data import CollectorData

class CollectorMetrics(Metrics):
    def __init__(self, collector: CollectorData):
        self.collector = collector
        self.metrics = {
            metric: metric.create_gauge()
            for metric in METRICS
        }

    async def collect(self):
        return self.metrics.values()
    
    async def update_metrics(self):
        data = await self.collector.get_metrics()
        for metric in METRICS:
            self.metrics[metric].labels(name=self.collector.name, id=self.collector.id).set(data[metric.json_key])
