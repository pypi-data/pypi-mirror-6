import sys

from setuptools import setup, find_packages

setup(
    name='ficloud-docker-utils',
    version='0.1.0',
    packages=find_packages(exclude=("test.*",)),

    url='https://github.com/pywizard/ficloud-docker-utils',
    license='MIT',
    author='Aleksandr Rudakov',
    author_email='ribozz@gmail.com',
    description='Tool that implements chef/puppet -like approach for server management.',
    long_description=open('README.md').read()
)
