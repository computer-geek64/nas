#!/bin/bash
# healthcheck.sh

set -e

mountpoint -q /var/www/html
ls /var/www/html

mountpoint -q /var/www/html/data/ashish/files
ls /var/www/html/data/ashish/files

mountpoint -q /var/www/html/data/melvin/files
ls /var/www/html/data/melvin/files

mountpoint -q /var/www/html/data/melvin/files
ls /var/www/html/data/melvin/files
