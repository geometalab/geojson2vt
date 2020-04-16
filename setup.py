from io import open
from setuptools import setup, find_packages

with open('README.rst', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='geojson2vt',
    version='1.0.0',
    description='Python package to convert GeoJSON to vector tiles',
    long_description=readme,
    author='Samuel Kurath',
    author_email='geometalab@hsr.ch',
    url='https://github.com/geometalab/geojson2vt',
    packages=find_packages(exclude=('tests', 'docs'))
)