try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Dfcapi',
    version='1.0.0',
    author='Debit Finance Collections Plc',
    author_email='development@debitfinance.co.uk',
    packages=['dfcapi'],
    url='https://github.com/dfcplc/dfcapi-python',
    license='LICENSE.txt',
    description='DFC Hosted Web Services - Python Client Library',
    install_requires=[
        "unirest >= 1.1.6"
    ]
)
