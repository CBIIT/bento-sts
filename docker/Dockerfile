FROM prefecthq/prefect-client:3.3.4.dev2-python3.11@sha256:f54420e24410a28c13b903cf0bb6342d4010755d6acb05bc13fa0431ad4d6f7e
EXPOSE 5000/tcp
ENV NEO4J_MDB_URI=bolt://localhost:7687 \
    NEO4J_MDB_USER=neo4j \
    NEO4J_MDB_PASS=neo4j1 \
    STS_PORT=5000 \
    STS_LOGLEVEL=info
ADD app /app
WORKDIR /app
RUN pip install bento-sts
RUN pip list | grep bento-sts > STS-VERSION
ENTRYPOINT ["gunicorn"]
