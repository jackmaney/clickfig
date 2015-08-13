from setuptools import setup, find_packages
from .clickfig import __version__

try:
    with open("requirements.txt") as f:
        requirements = [x.strip() for x in f if x.strip()]
except IOError as e:
    requirements = []

setup(
    name='clickfig',
    version=__version__,
    packages=find_packages,
    url='',
    license='MIT',
    author='Jack Maney',
    author_email='jackmaney@gmail.com',
    description='Simple Click-Based App Configuration',
    install_requires=requirements
)
