# bento-sts

Simple Terminology Service for [Bento MDB](https://github.com/CBIIT/bento-mdb).

The STS provides a web-based UI and a RESTful API for
browsing and accessing graph data models and associated controlled
vocabulary. See [https://cbiit.github.io/bento-meta/](https://cbiit.github.io/bento-meta/)
for an overview of the backend Metamodel Database (MDB). 

## Install

    pip install bento-sts

## Run

In the run directory, provide a `.env` file, with your appropriate
values for the environment variables given the the example file
[bento-sts.env.eg](./python/bento-sts.env.eg).

For testing:

    flask --app "bento_sts.sts:create_app()" run

For production, consider using
[gunicorn](https://docs.gunicorn.org/en/latest/index.html). [./src](./src)
contains two gunicorn config file examples, for development and production.

    gunicorn -c gunicorn.conf.dev.py

will start STS on a gunicorn server at http://localhost:8000.


## Dev Install

To work on bento-sts, make sure you have [Poetry](https://python-poetry.org/):

    pip install poetry

Then use it from the python working directory to install dependencies into a virtualenv:

    cd bento-sts/python
    poetry install

## Dev Model Database for Testing

The easiest way to provide a backend graph database for a local STS is to use Docker.
The following will get a workable model database running for STS development:

    docker pull maj1/test-mdb
    docker run -d -p7687:7687 --env NEO4J_AUTH=none --name test-mdb maj1/test-mdb

Then set the following in your src/.env file:

    NEO4J_MDB_URI=bolt://localhost:7867
    NEO4J_MDB_USER=neo4j
    NEO4J_MDB_PASS=neo4j
    STS_LOGFILE=./sts.log

## Run Local STS

Once the database is running and configured, start the local STS as follows:

    cd bento-sts/python/src
    poetry run flask --app "bento_sts.sts:create_app()" run

You should be able to see the frontend on your machine at http://localhost:5000.

## API Docs

The API is documented in an [OpenAPI (Swagger) schema](/swagger/swagger.yaml). 

Docker is probably the easiest way to run a local Swagger server. 
This will bring up a Swagger server at port 6000:

    # from the repo root, run...
    docker run -p 6000:8080 -e SWAGGER_JSON=/work/swagger.json -v ${PWD}/swagger:/work docker.swagger.io/swaggerapi/swagger-ui

(see [https://swagger.io/docs/open-source-tools/swagger-ui/usage/installation/](https://swagger.io/docs/open-source-tools/swagger-ui/usage/installation/))
