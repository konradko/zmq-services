from distutils.core import setup
from setuptools import find_packages

setup(
    name='zmqservices',
    version='0.1.5',
    url='https://github.com/konradko/zmq-services',
    packages=find_packages(),
    long_description=open('README.md').read(),
    install_requires=[
        'pyzmq==15.4.0',
    ],
)
