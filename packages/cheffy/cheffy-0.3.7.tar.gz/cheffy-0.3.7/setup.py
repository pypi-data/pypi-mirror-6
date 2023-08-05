from setuptools import setup, find_packages
from cheffy import __version__


setup(
    name='cheffy',
    version=__version__,
    author='Roman Dashevsky',
    author_email='dashevsky@selectel.ru',
    packages=find_packages(),
    url='https://pypi.python.org/pypi/cheffy',
    license='LICENSE',
    description='A simple requests based wrapper for a Chef server api.',
    long_description=open('README').read(),
)
