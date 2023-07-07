#!/bin/bash

if test "$1" = ""; then
  echo "missing relay number"
  echo "Usage: $0 <relay_number>"
  exit 1
fi

docker run -dit --name relay$1 --net net1 -e HOST_IP=$(ipconfig getifaddr en0) -e SERVICE_NAME=relay$1 --cpuset-cpus=$i python
docker cp ./relay/ relay$1:/src/
docker exec -d relay$1 sh -c "python3 /src/service.py"
