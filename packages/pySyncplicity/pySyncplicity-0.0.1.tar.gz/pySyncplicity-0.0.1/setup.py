import os
from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name="pySyncplicity",
    version="0.0.1",
    author="Matt Cowger",
    author_email="matt@cowger.us",
    description=("A python module to interact with EMC Syncplicity"),
    license="BSD",
    long_description=readme(),
    keywords="syncplicity",
    include_package_data=True,
    url="http://packages.python.org/pysyncplicity",
    packages=['pySyncplicity','pySyncplicity.urls'],
    install_requires=[
        'requests',
        'requests-toolbelt'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
    ],
)