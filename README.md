# bento-sts

Simple Terminology Service for [Bento MDB](https://github.com/CBIIT/bento-mdb).

See [bento-meta documentation] for an overview of the Metamodel
Database. The STS provides a web-based UI and a RESTful API for
browsing and accessing graph data models and associated controlled
vocabulary.

## Install

    pip install bento-sts

## Run

In the run directory, provide a `.env` file, with your appropriate
values for the environment variables given the the example file
[bento-sts.env.eg](./python/bento-sts.env.eg).

For testing:

    flask --app "bento_sts.sts:create_app()" run

## API Docs



