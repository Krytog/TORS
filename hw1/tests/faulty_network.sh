#!/bin/bash

cd ..

docker-compose exec worker2 iptables -A INPUT -m statistic --mode random --probability 1 -j DROP
sleep 10

docker-compose exec worker4 iptables -A INPUT -m statistic --mode random --probability 1 -j DROP
