#!/bin/bash
# install.sh

export PATH="$PATH:/usr/local/bin"

mkdir -p /data/nas
mkdir -p /data/nas/family
mkdir -p /data/nas/windows_backup
chown -R 33:33 /data/nas/family
chown -R 33:33 /data/nas/windows_backup

docker pull nextcloud
docker pull postgres

docker volume create nas-redis-data
docker volume create nas-postgres-data

read -sp 'PostgreSQL password: ' POSTGRES_PASSWORD
docker run -d --network=bridge -e "POSTGRES_DB=nextcloud" -e "POSTGRES_USER=nextcloud" -e "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" -v nas-postgres-data:/var/lib/postgresql/data --name postgres --rm postgres
docker run -d --network=bridge -e "POSTGRES_HOST=postgres" -e "POSTGRES_DB=nextcloud" -e "POSTGRES_USER=nextcloud" -e "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" -v /data/nas/nextcloud:/var/www/html -v /data/nas/users:/data/users --name nextcloud --rm nextcloud
echo "Finish Nextcloud initialization"
echo "Open http://localhost/ and create account for each user (and login too)"
echo "Edit config/config.php to contain \"'filesystem_check_changes' => 1,\" and add 'nextcloud' to \"trusted_domains\""
read -p 'Press enter when ready to proceed...'

docker container exec nextcloud mv /var/www/html/data/ashish/files /data/users/ashish
docker container exec nextcloud mv /var/www/html/data/melvin/files /data/users/melvin
docker container exec nextcloud mv /var/www/html/data/joy/files /data/users/joy
docker container stop nextcloud
docker container stop postgres

docker-compose build --no-cache
docker-compose up -d samba

echo "Set ashish's password:"
docker container exec -it nas-samba smbpasswd -a ashish
echo "Set melvin's password:"
docker container exec -it nas-samba smbpasswd -a melvin
echo "Set joy's password:"
docker container exec -it nas-samba smbpasswd -a joy

docker-compose down
