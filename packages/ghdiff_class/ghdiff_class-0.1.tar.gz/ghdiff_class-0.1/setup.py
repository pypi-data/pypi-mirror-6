#!/usr/bin/env python

from setuptools import setup

setup(
    name="ghdiff_class",
    description="Generate pretty Github-style diffs (class version, see ghdiff for origin)",
    version="0.1",
    author="Stephane 'Twidi' Angel",
    author_email="s.angel@twidi.com",
    url="http://github/twidi/ghdiff",
    license="MIT",
    package_data={"": ["*.py", "*.txt", "*.css"]},
    include_package_data=True,
    package_dir={"": "src"},
    py_modules=["ghdiff"],
    tests_require=["zope.testrunner"],
    install_requires=["six", "chardet"],
    test_suite="tests.test_suite"
    )
