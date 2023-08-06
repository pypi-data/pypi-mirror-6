import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    test_suite = 'browser_compare.tests',
    name = "browser_compare",
    version = "0.0.1",
    author = "Olli Jarva",
    author_email = "olli@jarva.fi",
    description = ("Library for detecting browser changes"),
    license = "MIT",
    keywords = "browser user-agent",
    url = "https://github.com/ojarva/browser-compare",
    packages=['browser_compare'],
    long_description=read('README.rst'),
    install_requires=["httpagentparser>=1.6.0"],
    download_url = "https://github.com/ojarva/browser-compare",
    bugtracker_url = "https://github.com/ojarva/browser-compare/issues",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
    ],
)
