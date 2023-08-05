
#from distutils.core import setup

from __future__ import print_function
from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))

def find_version(path):
    version = ""
    path = os.path.join(here,path)

    with file(path) as f:
        for line in f:
            if line.startswith('__version__'):
                _,version = line.replace(" ",'').split("=")
                version = version[1:len(version)-2]
                break 

    if version:
        return version
    raise RuntimeError("Unable to find version.")

version = find_version('pymd.py')

setup(
    name = "pymd",
    version = version,
    description = "wrapper for python markdown but having a full HTML for the output (and nice things)",
    long_description=(open('README.txt').read() + '\n\n' +
                    open('CHANGELOG.txt').read()),
    author = "Ei Kiu",
    author_email = "eikiu.inc@gmail.com",
    url = "https://github.com/eikiu/pymd",
    keywords = "markdown, html",
    license = "MIT",
	include_package_data=True,
    py_modules=['pymd'],
    zip_safe = False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
		"Topic :: Documentation",
		"Topic :: Software Development :: Documentation",
		"Topic :: Text Processing",
		"Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
    ],
	
	install_requires=['Markdown>=2.0']
	
)

