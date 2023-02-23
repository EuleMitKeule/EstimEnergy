#! /usr/bin/env bash

# This script runs the API server.

uvicorn estimenergy.main:app --reload --port 8000