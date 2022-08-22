#!/bin/bash
# uninstall.sh

docker-compose down

docker volume rm nas-redis-data

rm -rf /data/nas
