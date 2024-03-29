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

docker volume create nas-samba-data
docker volume create nas-nextcloud-data
docker volume create nas-redis-data
docker volume create nas-postgres-data

POSTGRES_PASSWORD="$(uuidgen -r)"
docker network create nas-nextcloud-postgres
docker run -d --network=nas-nextcloud-postgres -e "POSTGRES_DB=nextcloud" -e "POSTGRES_USER=nextcloud" -e "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" -v nas-postgres-data:/var/lib/postgresql/data --name postgres --rm postgres
docker run -d --network=nas-nextcloud-postgres -p 80:80 -e "POSTGRES_HOST=postgres" -e "POSTGRES_DB=nextcloud" -e "POSTGRES_USER=nextcloud" -e "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" -v nas-nextcloud-data:/var/www/html -v /data/nas/users:/data/users --name nextcloud --rm nextcloud

echo "Open https://nas.homelab.net/ and create a Nextcloud account for each user (and login too)"
echo "Edit config/config.php and add 'nextcloud' to 'trusted_domains'"
echo "Add the following lines as well:"
echo "'overwritehost' => 'nas.homelab.net',"
echo "'overwriteprotocol' => 'https',"
echo "'overwritewebroot' => '/nextcloud',"
echo "'overwrite.cli.url' => 'https://nas.homelab.net/nextcloud',"
echo "'filesystem_check_changes' => 1,"
read -p 'Press enter when ready to proceed...'

docker container exec nextcloud mv /var/www/html/data/ashish/files /data/users/ashish
docker container exec nextcloud mv /var/www/html/data/melvin/files /data/users/melvin
docker container exec nextcloud mv /var/www/html/data/joy/files /data/users/joy

docker container stop nextcloud
docker container stop postgres
docker network rm nas-nextcloud-postgres

docker-compose build --no-cache

docker run -d --network=none -v nas-samba-data:/data --name samba --rm nas_samba

echo "Set ashish's password:"
docker container exec -it samba smbpasswd -a ashish
echo "Set melvin's password:"
docker container exec -it samba smbpasswd -a melvin
echo "Set joy's password:"
docker container exec -it samba smbpasswd -a joy

docker container exec -it samba sh -c 'mv /var/lib/samba/* /data'

docker container stop samba
