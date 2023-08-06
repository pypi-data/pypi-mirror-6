# coding: utf-8
from setuptools import setup
import os
requires_list = ["yamlish"]


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as inf:
        return "\n" + inf.read().replace("\r\n", "\n")

setup(
    name='bayeux',
    version="0.8",
    description='Generator of the TAP protocol',
    author=u'Matěj Cepl',
    author_email='mcepl@cepl.eu',
    url='http://luther.ceplovi.cz/git/?p=bayeux.git',
    py_modules=['tap', 'unittest_TAP'],
    scripts=['generate_TAP'],
    long_description=read("README.txt"),
    keywords=['TAP', 'unittest'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    test_suite="test.test_tap",
    install_requires=requires_list,
)
