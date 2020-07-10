FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    make \
    perl \
    cpanminus \
    carton


EXPOSE 3000
WORKDIR /app/

COPY cpanfile /app/cpanfile
COPY cpanfile.snapshot /app/cpanfile.snapshot
RUN carton install

COPY lib /app/lib
COPY script /app/script
COPY templates /app/templates
COPY bento-sts.conf /app/bento-sts.conf
COPY run.sh /app/run.sh
WORKDIR /app
CMD ["/app/run.sh"]
