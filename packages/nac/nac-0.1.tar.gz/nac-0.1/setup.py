import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)).read()

setup(
    name = "nac",
    version = "0.1",
    author = "Tomasz Ducin",
    author_email = "tomasz.ducin@gmail.com",
    description = "Noughts and Crosses (aka Tic Tac Toe) game implementation",
    license = "MIT",
    keywords = "game",
    url = "https://github.com/tkoomzaaskz/noughts-and-crosses",
    packages = ['nac'],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License"
    ],
    long_description = read('README.rst'),
)
