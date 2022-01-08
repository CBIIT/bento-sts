# Welcome to pysts

This is a flask-based implementation of the Simple Terminology Service (STS) for the Bento Metadatabase (MDB).

## Install

	$ git clone https://github.com/CBIIT/bento-sts.git
	$ cd pysts
	$ virtualenv sts-venv
	$ source sts-venv/bin/activate
	$ pip install -r requirements.txt
	$ flask run

## Dependencies

`bento-sts` requires an Elastic store and a Neo4j-based
[MDB](https://github.com/CBIIT/bento-meta).

For authentication, a user database must be set up.

For email-based password reset, the server must have email
capabilities.



