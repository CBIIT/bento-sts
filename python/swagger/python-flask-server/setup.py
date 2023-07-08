# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["connexion"]

setup(
    name=NAME,
    version=VERSION,
    description="Simple Terminology Server API",
    author_email="mark.jensen@nih.gov",
    url="",
    keywords=["Swagger", "Simple Terminology Server API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    The Simple Terminology Server (STS) exposes elements of data models in an intuitive, consistent way. Data models expressed in the form of a [property graph](https://en.wikipedia.org/wiki/Graph_database#Labeled-property_graph) -- i.e., as nodes, relationships, properties, and terms -- can be explored and queried via this interface. Data models are stored in an instance of a [Metamodel Database (MDB)](https://github.com/CBIIT/bento-meta) backed by a [Neo4j](https://neo4j.com) server.
    """
)

