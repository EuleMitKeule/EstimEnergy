[![PyPI](https://img.shields.io/pypi/v/estimenergy)](https://pypi.org/project/estimenergy)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

[![Docker](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/docker.yml/badge.svg)](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/docker.yml)
[![PyPI](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/pypi.yml/badge.svg)](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/pypi.yml)
[![HACS](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/hacs.yml/badge.svg)](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/hacs.yml)
[![hassfest](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/hassfest.yml/badge.svg)](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/hassfest.yml)

# EstimEnergy

EstimEnergy is tool for monitoring and estimating energy usage and cost.
It consists of a FastAPI application that collects data from a home-assistant-glow device and a HACS enabled custom integration for Home Assistant that exposes the data via a sensor entity.

## Installation

Create the following directories:

`/path/to/appdata/estimenergy/config`<br>
`/path/to/appdata/estimenergy/prometheus`

Create a configuration file named `config.yml` in the config directory. Change the values of the example configuration according to your energy contract. You can read more about the specific options below.

```yaml
# config.yml

collectors:
  - name: glow
    host: "192.168.0.123"
    port: 6053
    password: ""
    cost_per_kwh: 0.1234
    base_cost_per_month: 12.34
    payment_per_month: 123.4
    billing_month: 1
    min_accuracy: 0.75
```

Now you can deploy the application stack using this example docker-compose configuration.
Change the mounting paths according to where you created the corresponding directories.

```yaml
# docker-compose

services:
  estimenergy:
    image: ghcr.io/eulemitkeule/estimenergy:latest
    container_name: estimenergy
    volumes:
      - /path/to/appdata/estimenergy/config:/config
      
  estimenergy-prometheus:
    image: prom/prometheus:latest
    container_name: estimenergy-prometheus
    command:
        - --storage.tsdb.retention.time=5y
        - --storage.tsdb.retention.size=1TB
    volumes:
      - /path/to/appdata/estimenergy/prometheus:/prometheus
```

Now you should have the EstimEnergy API running on port `12321` and a prometheus collector running at port `9090`. 

Prometheus will scrape the metrics exposed by EstimEnergy every 15 seconds and keep the data for five years or until 1TB of space is used. This can be configured via the `--storage.tsdb.retention.time` and `--storage.tsdb.retention.size` command options in the docker-compose file.

To test out whether everything works correctly and the data is being collected you can configure the prometheus data source in Grafana and use the provided [dashboard](dashboard.json). After importing the dashboard you will have to change the dashboards variables to use your collector and data source. 

## Home Assistant Integration

Install the repository in HACS via the custom repository option. After restarting Home Assistant you can add and configure the integration in the integrations UI. You need to provide the hostname or IP of the EstimEnergy docker container and the port on which it is running on.

This will create sensor entities for each collector and each metric that is being collected. You can use the `Total Energy` and `Yearly Cost` entities as data sources for the Home Assistant Energy Dashboard.

## Specification

#### `config.yml`
|option|type|description|
|-|-|-|
|collectors|`list`|Configure one or multiple energy collectors

#### `collectors`
option|type|description
-|-|-
name|`str`|User defined name for the collector
host|`str`|The hostname or IP of the collector
port|`int`|The port of the collector
password|`str`|The password of the collector configured in ESPHome
cost_per_kwh|`float`|Money spent per kilowatt hour used
base_cost_per_month|`float`|Usage independent cost per month
payment_per_month|`float`|Money prepaid per month
billing_month|`int`|Month in which the billing period begins
min_accuracy|`float`|Minimum accuracy required to avoid estimating the month or day
