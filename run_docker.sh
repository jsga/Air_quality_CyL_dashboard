#!/usr/bin/env bash

echo killing old docker processes
docker-compose down -v

echo building docker containers
docker-compose up --build -d

