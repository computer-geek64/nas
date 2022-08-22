#!/bin/bash
# uninstall.sh

docker-compose down

docker volume rm nas-redis-data
docker volume rm nas-postgres-data

rm -rf /data/nas
