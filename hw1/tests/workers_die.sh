#!/bin/bash

cd ..

docker-compose stop -t 1 worker2
sleep 10

docker-compose stop -t 1 worker3
