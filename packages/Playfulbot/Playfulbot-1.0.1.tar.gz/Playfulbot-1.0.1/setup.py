# -*- coding: utf-8 -*-
#
# 2014 Alex Silva <alexsilvaf28 at gmail.com>

"""
Usage:
    python setup.py install
"""

from ez_setup import use_setuptools

use_setuptools()

from setuptools import setup

setup(
	name="Playfulbot",
	description="Playfulbet auto-bet",
	version="1.0.1",
	author="Alex Silva",
	author_email="h4ll0ck at gmail dot com",
	url="https://github.com/Alexsays/Playfulbot",
	license="GNU General Public License (GPLv2)",
	scripts=['playfulbot.py'],
	install_requires=[
		"mechanize",
		"beautifulsoup4"
	]
)
