#!/bin/bash
# uninstall.sh

export PATH="$PATH:/usr/local/bin"

docker-compose down

docker volume rm nas-samba-data
docker volume rm nas-redis-data
docker volume rm nas-postgres-data

rm -rf /data/nas
