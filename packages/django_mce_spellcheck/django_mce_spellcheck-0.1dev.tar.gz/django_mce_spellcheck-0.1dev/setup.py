import os
import sys

from setuptools import setup, find_packages

version = '0.1'

setup(name='django_mce_spellcheck',
    description='Django app that provides a backend for the tinymce spellcheck plugin. Particularly useful for Mezzanine',
    long_description='Django app that provides a backend for the tinymce spellcheck plugin. Particularly useful for Mezzanine',
    version=version,
    author = "Sean O\'Donnell",
    author_email = "sean@odonnell.nu",
    url = "https://github.com/seanodonnell/django_mce_spellcheck",
    download_url = "https://github.com/seanodonnell/django_mce_spellcheck/archive/master.zip",
    keywords = ["django", "tinymce", "spellcheck", "mezzanine"],
    packages=find_packages(exclude=['ez_setup']),
        classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
    ],
    include_package_data=True,
    zip_safe=False,
)
