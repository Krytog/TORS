FROM ubuntu

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake

WORKDIR /TORS
COPY . .

RUN cmake . && make master && make worker
