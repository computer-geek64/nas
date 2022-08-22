#!/bin/bash
# healthcheck.sh

set -e

mountpoint -q /data/family
ls /data/family

mountpoint -q /home
ls /home

mountpoint -q /data/windows_backup
ls /data/windows_backup

ps -ef | grep 'smbd'
