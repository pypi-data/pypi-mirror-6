import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = __import__('subdownloader').get_version()

setup(
	name = "subdownloaderlite",
	version = version,
	data_files=[
		('', ['subdownloader-lite.json'])
	],
	author = "Gabriel Melillo",
	author_email = "gabriel@melillo.me",
	description = ("A simple command line tool to search and download subtitles from opensubtitles.org "),
	license = "GPLv3",
	url = "https://pypi.python.org/pypi/subdownloaderlite/",
	packages = find_packages('.'),
	scripts = ['subdownloader-lite',],
	include_package_data=True,
)
