FROM python:3.9

WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY logging.yml logging.yml
COPY README.md README.md
COPY estimenergy estimenergy

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

ENV CONFIG_PATH /config/config.yml
ENV DB_PATH /config/estimenergy.db
ENV ENABLE_METRICS true

VOLUME /config

CMD ["poetry", "run", "uvicorn", "estimenergy.main:app", "--host", "0.0.0.0", "--port", "80", "--log-config", "logging.yml"]