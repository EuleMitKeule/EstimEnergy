
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Docker](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/docker.yml/badge.svg)](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/docker.yml)
[![PyPI](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/pypi.yml/badge.svg)](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/pypi.yml)
[![HACS](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/hacs.yml/badge.svg)](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/hacs.yml)
[![hassfest](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/hassfest.yml/badge.svg)](https://github.com/EuleMitKeule/EstimEnergy/actions/workflows/hassfest.yml)

# EstimEnergy

EstimEnergy is tool for monitoring and estimating energy usage and cost.
It consists of a FastAPI application that collects data from a home-assistant-glow device, an accompanying API client library and a HACS enabled custom integration for Home Assistant that exposes the data via a sensor entity.

## EstimEnergy API

### Installation

```yaml
# docker-compose

services:
  estimenergy:
    image: ghcr.io/eulemitkeule/estimenergy:latest
    container_name: estimenergy
    restart: unless-stopped
    ports:
      - 12380:80
    volumes:
      - /path/to/appdata/estimenergy:/config
```

The mounted folder must contain a `config.yml` file that is used to integrate and configure home-assistant-glow devices.

### Configuration

```yaml
# config.yml

collectors:
  - name: <name_your_glow_device> # "glow"
    host: <glow_device_ip_address> # 192.168.0.123
    port: <glow_device_ip_address> # 6053
    password: <glow_device_password> # ""
    cost_per_kwh: <cost_per_kilowatt_hour> # 0.1234
    base_cost_per_month: <independent_cost_per_month> # 12.34
    payment_per_month: <monthly_payment_in_advance> # 123.4
    billing_month: <month_the_billing_period_begins> # 9
    max_incomplete_days: <explained_below> # 5
    min_hour: <explained_below> # 0
    max_hour: <explained_below> # 24
```

## EstimEnergy Library

### Installation

```sh
pip install estimenergy
```

### Usage

```python
from estimenergy.client import EstimEnergyClient

client = EstimEnergyClient(
    host="<estimenergy_api_ip_address",
    port=<estimenergy_api_port>
)

data = client.get_data(name="<glow_device_name>")
```

## Home Assistant Integration

### Installation

Install the repository in HACS via custom repository option. After restarting Home Assistant you can add and configure the integration via the integrations UI.