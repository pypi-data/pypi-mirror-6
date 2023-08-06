from distutils.core import setup
from setuptools import find_packages

setup(
    name="bashplotlib",
    version="0.5.2",
    author="Greg Lamp",
    author_email="lamp.greg@gmail.com",
    url="https://github.com/glamp/bashplotlib",
    license="MIT",
    packages=find_packages(),
    description="plotting in the terminal",
    long_description=open("README.rst").read(),
    scripts=['bin/hist', 'bin/scatter'],
)

