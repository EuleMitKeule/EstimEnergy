FROM python:3.10 as generate-openapi

WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY README.md README.md
COPY estimenergy estimenergy

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
RUN poetry run generate-openapi

FROM node:18.16.0-alpine as build-frontend

WORKDIR /app

COPY estimenergy-web/ .
COPY --from=generate-openapi /app/openapi.json openapi.json

RUN apk add --no-cache openjdk11
RUN npm install
RUN npm run generate-openapi -- -i openapi.json
RUN npm run build

FROM nginx/unit:1.29.1-python3.11

WORKDIR /app

COPY --from=build-frontend /app/dist/estimenergy-web estimenergy-web
COPY pyproject.toml pyproject.toml
COPY README.md README.md
COPY estimenergy estimenergy
COPY unit-config.json /docker-entrypoint.d/config.json

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
RUN mkdir /config
RUN chown -R www-data:www-data /config

ENV CONFIG_PATH /config/config.yml

VOLUME /config
EXPOSE 12321
