from setuptools import setup
import os

with open('README.md') as file:
    long_description = file.read()

setup(
    name = "colossus",
    version = "0.0.1",
    author = "Steve Leibman",
    author_email = "sleibman@alum.mit.edu",
    description = ("Python tools for manipulating extremely large images"),
    license = "MIT",
    keywords = "large images",
    url = "https://github.com/sleibman/python-colossus",
    packages = ['colossus',
                'colossus.test'],
    include_package_data = True,
    package_data = {'colossus': ['README.md', 'LICENSE.txt']},
    long_description = long_description,
    test_suite = 'colossus.test',
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
    ],
)
