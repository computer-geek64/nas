#!/bin/bash
# install.sh

mkdir -p /data/nas
mkdir -p /data/nas/family
mkdir -p /data/nas/windows_backup
chown -R 33:33 /data/nas/family
chown -R 33:33 /data/nas/windows_backup

docker volume create nas-redis-data

docker pull nextcloud

docker run -d --network=host -v /data/nas/nextcloud:/var/www/html -v /data/nas/users:/data/users --name nextcloud --rm nextcloud
echo "Finish Nextcloud initialization"
echo "Open http://localhost/ and create account for each user (and login too)"
echo "Edit config/config.php to contain \"'filesystem_check_changes' => 1,\" and add 'nextcloud' to \"trusted_domains\""
read -p 'Press enter when ready to proceed...'

docker container exec nextcloud mv /var/www/html/data/ashish/files /data/users/ashish
docker container exec nextcloud mv /var/www/html/data/melvin/files /data/users/melvin
docker container exec nextcloud mv /var/www/html/data/joy/files /data/users/joy
docker container stop nextcloud

docker-compose build --no-cache
docker-compose up -d samba

echo "Set ashish's password:"
docker container exec -it nas-samba smbpasswd -a ashish
echo "Set melvin's password:"
docker container exec -it nas-samba smbpasswd -a melvin
echo "Set joy's password:"
docker container exec -it nas-samba smbpasswd -a joy

docker-compose down
