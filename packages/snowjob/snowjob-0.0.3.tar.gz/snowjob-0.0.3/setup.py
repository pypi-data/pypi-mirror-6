import os
import platform

from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requires = []

if platform.system() == 'Windows':
    requires.append('colorama')

setup(
    name="snowjob",
    version="0.0.3",
    author="John Anderson",
    author_email="sontek@gmail.com",
    description=("A python script that will make your terminal "
                 "snow"),
    license = "BSD",
    install_requires=requires,
    keywords="",
    url = "http://github.com/sontek/snowjob",
    packages=['snowjob'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points = {
        'console_scripts': [
            'snowjob = snowjob:main',
        ],
    }
)
