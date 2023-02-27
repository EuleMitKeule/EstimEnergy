
import os
from setuptools import setup

version = os.environ.get("RELEASE_VERSION", None)

setup(
    name='estimenergy_client',
    version=version,
    description='Client for the Estimenergy API',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eulemitkeule/estimenergy',
    author='Lennard Beers',
    author_email='l.beers@outlook.de',
    keywords='estimenergy api client',
    packages=['estimenergy_client'],
    python_requires='>=3.6',
    install_requires=[
        'requests',
    ],
)