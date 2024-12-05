FROM ubuntu

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    iputils-ping \
    iproute2 \
    net-tools \
    iptables

WORKDIR /TORS
COPY . .

RUN cmake . && make master && make worker
