from setuptools import setup, find_packages
from pglogs import __version__

setup(
    name='pglogs',
    version=__version__,
    author='Roman Dashevsky',
    author_email='dashevsky@selectel.ru',
    packages=find_packages(),
    url='https://github.com/romario8/pglogs',
    license='LICENSE',
    description='A simple lib for postgres logging',
    long_description=open('README').read(),
    install_requires=[
        'Flask >= 0.9',
        'psycopg2'
    ]
)
