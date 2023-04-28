[![PyPI](https://img.shields.io/pypi/v/estimenergy)](https://pypi.org/project/estimenergy)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

[![Publish](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/publish.yml/badge.svg)](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/publish.yml)
[![Code Quality](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/quality.yml/badge.svg)](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/quality.yml)

# EstimEnergy

EstimEnergy is tool for monitoring and estimating energy usage and cost.
It consists of a FastAPI backend that collects data from a device, an Angular frontend for configuration and a HACS enabled custom integration for Home Assistant that exposes the data via a sensor entity.

## Installation

Create the following directories:

`/path/to/appdata/estimenergy/config`<br>
`/path/to/appdata/estimenergy/postgresql`<br>
`/path/to/appdata/estimenergy/influxdb`<br>
`/path/to/appdata/estimenergy/prometheus`

Create a configuration file named `config.yml` in the config directory.

```yaml
db:
  url: "postgresql://estimenergy:<db-password>@estimenergy-postgresql:5432/estimenergy?sslmode=disable"

influxdb:
  url: http://estimenergy-influxdb:8086
  org: estimenergy
  token: <influx-token>
  bucket: estimenergy
```

Now you can deploy the application stack using the example [docker-compose](docker-compose.yml) configuration.
Add mounting paths according to where you created the corresponding directories.

Using InfluxDB and Prometheus is optional. If you don't want to use InfluxDB, you need to remove the configuration from the `config.yml` file.

Postgres is also optional and can be replaced with any other SQL database including SQLite. If you want to use SQLite, you need to change to database URL in the config file to `sqlite:////config/estimenergy.db`. Using an external database is recommended, since the Grafana dashboard needs to access the database directly.

```yaml
# docker-compose

services:
  estimenergy:
    # ...
    volumes:
      - /path/to/appdata/estimenergy/config:/config

  estimenergy-postgresql:
    # ...
    volumes:
      - /path/to/appdata/estimenergy/postgresql:/var/lib/postgresql/data

  estimenergy-influxdb:
    # ...
    volumes:
      - /path/to/appdata/estimenergy/influxdb:/var/lib/influxdb2

  estimenergy-prometheus:
    # ...
    volumes:
      - /path/to/appdata/estimenergy/prometheus:/prometheus
```

Now you should have EstimEnergy running on port `12321`, a prometheus collector running at port `9090`, InfluxDB at port `8086` and PostgreSQL at port `5432`.

Prometheus will scrape the metrics exposed by EstimEnergy every 15 seconds and keep the data for five years or until 1TB of space is used. This can be configured using the `--storage.tsdb.retention.time` and `--storage.tsdb.retention.size` command options in the docker-compose file.

You should now be able to access the web UI at port 12321. You will have to create one or more devices and configure them using your energy contract data.

## Home Assistant Integration

Install the repository in HACS via the custom repository option. After restarting Home Assistant you can add and configure the integration in the integrations UI. You need to provide the hostname or IP of the EstimEnergy docker container and the port on which it is running on.

This will create sensor entities for each collector and each metric that is being collected. You can use the `Total Energy` and `Total Cost` entities as data sources for the Home Assistant Energy Dashboard.

## Specification

#### `config.yml`
|option|type|description|
|-|-|-|
|db|`dict`|Database configuration|
|db.url|`str`|Database URL|
|influxdb|`dict`|InfluxDB configuration|
|influxdb.url|`str`|InfluxDB URL|
|influxdb.org|`str`|InfluxDB organization|
|influxdb.token|`str`|InfluxDB token|

#### `device`
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
