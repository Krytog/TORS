#!/bin/bash

cd ..

docker-compose stop -t 1 worker2
sleep 2

docker-compose stop -t 1 worker3
sleep 15

docker-compose restart worker2
