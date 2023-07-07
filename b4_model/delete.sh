#!/bin/bash

if test "$1" = ""; then
  echo "missing number of services"
  echo "Usage: $0 <num_services>"
  exit 1
fi

B4_MODEL_PATH="/Users/saito/Desktop/sfc_test_june/b4_model"
HOST_IP=$(ipconfig getifaddr en0)
NUM_RELAIES=$1

docker rm -f producer consumer

for ((i=1; i<=$NUM_RELAIES; i++))
do
  cd $B4_MODEL_PATH/relay$i/ && \
    docker-compose down -v
  rm -r $B4_MODEL_PATH/relay$i/
done

rm $B4_MODEL_PATH/topology/*
