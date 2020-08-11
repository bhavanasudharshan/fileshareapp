#!/bin/sh

docker build  --no-cache  -f ../usersapi/Dockerfile -t usersapi ../../usersapi

docker build  --no-cache  -f ../filedownload/Dockerfile -t filedownload ../../filedownload

docker build  --no-cache  -f ../Dockerfile -t fileshareapp .