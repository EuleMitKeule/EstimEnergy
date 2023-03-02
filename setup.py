
import os
from setuptools import setup

version = os.environ.get("RELEASE_VERSION", None)

setup(
    name='estimenergy',
    version=version,
    description='EstimEnergy Python Package',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/EuleMitKeule/EstimEnergy',
    author='Lennard Beers',
    author_email='l.beers@outlook.de',
    keywords='estimenergy api client',
    packages=['estimenergy'],
    python_requires='>=3.6',
    install_requires=[
        "requests",
        "uvicorn[standard]",
        "fastapi",
        "fastapi-crudrouter",
        "httpx",
        "aioesphomeapi",
        "tortoise_orm",
        "prometheus_client",
        "prometheus-fastapi-instrumentator",
        "python-dotenv",
    ],
)