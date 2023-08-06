import os
from setuptools import setup, find_packages


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='bernoulli_django',
    version='0.1.4',
    packages=find_packages(),
    license='MIT',
    description='Package to integrate django app with Bernoulli',
    url='https://github.com/bernoulli-metrics/bernoulli_django',
    author='Joe Gasiorek',
    author_email='joe.gasiorek@gmail.com',
    install_requires=['bernoulli>=0.1.3']
)
