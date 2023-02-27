
from setuptools import setup


setup(
    name='estimenergy_client',
    version='0.1.0',
    description='Client for the Estimenergy API',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eulemitkeule/estimenergy',
    author='Lennard Beers',
    author_email='l.beers@outlook.de',
    keywords='estimenergy api client',
    packages=['estimenergy_client'],
    python_requires='>=3.6',
)