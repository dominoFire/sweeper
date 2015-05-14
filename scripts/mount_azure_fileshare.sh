#! /bin/bash

# EXAMPLE variables
STORAGE_ACCOUNT_NAME='sweeperdfs'
STORAGE_ACCOUNT_KEY='x3ZmnPEZnVlatAXsvt1e7X0RZjOOxR3iwYo1rX6e0TmTaGpbNg4B/NXaSrr64ji4vTASH7UDyNzjRSSlD6xJtQ=='
FILESHARE_NAME='fileshare'
FILESHARE_PATH="//${STORAGE_ACCOUNT_NAME}.file.core.windows.net/${FILESHARE_NAME}"

sudo chown azureuser /opt
mkdir -p /opt/fileshare

sudo mount $FILESHARE_PATH /opt/fileshare \
    -t cifs \
    -o "vers=2.1,dir_mode=0777,file_mode=0777,username=${STORAGE_ACCOUNT_NAME},password=${STORAGE_ACCOUNT_KEY}"
