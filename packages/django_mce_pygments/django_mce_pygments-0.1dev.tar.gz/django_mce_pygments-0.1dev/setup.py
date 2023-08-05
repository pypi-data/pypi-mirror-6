import os
import sys

from setuptools import setup, find_packages

version = '0.1'

setup(name='django_mce_pygments',
    description='Django app that provides a pygments plugin for tinymce and backend functionality. Particularly useful for Mezzanine',
    long_description='Django app that provides a pygments plugin for tinymce and backend functionality. Particularly useful for Mezzanine',
    author = "Sean O\'Donnell",
    author_email = "sean@odonnell.nu",
    url = "https://github.com/seanodonnell/django_mce_pygments",
    download_url = "https://github.com/seanodonnell/django_mce_pygments/archive/master.zip",
    keywords = ["django", "tinymce", "pygments", "mezzanine"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
    ],
    version=version,
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
)
