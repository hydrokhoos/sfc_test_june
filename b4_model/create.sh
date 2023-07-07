#!/bin/bash

if test "$1" = ""; then
  echo "missing number of services"
  echo "Usage: $0 <num_services>"
  exit 1
fi

B4_MODEL_PATH="/Users/saito/Desktop/sfc_test_june/b4_model"
HOST_IP=$(ipconfig getifaddr en0)
NUM_RELAIES=$1

## containers
python3 $B4_MODEL_PATH/cp_docker-compose.py $NUM_RELAIES

docker run -dit --name producer --privileged -v $B4_MODEL_PATH/topology/:/topology/ -p $HOST_IP:16363:6363 --cpuset-cpus 4 hydrokhoos/ndn-all:arm
docker run -dit --name consumer --privileged -v $B4_MODEL_PATH/topology/:/topology/ -p $HOST_IP:26363:6363 --cpuset-cpus 5 hydrokhoos/ndn-all:arm

docker cp ../img.jpg producer:/img.jpg

for ((i=1; i<=$NUM_RELAIES; i++))
do
  cd $B4_MODEL_PATH/relay$i/ && \
    docker-compose up -d
done


## nfd & nlsr
docker exec producer sh -c "nfd-start 2> /nfd.log"
sleep 0.1
docker exec producer nfdc cs config capacity 0
docker exec -d producer nlsr -f /topology/producer-nlsr.conf
docker exec producer nlsrc advertise /img.jpg
docker exec -d producer sh -c "ndnputchunks /img.jpg < /img.jpg"

for ((i=1; i<=$NUM_RELAIES; i++))
do
  PORT=$(printf "636%02d" $i)
  docker exec relay$i-sidecar-1 sh -c "nfd-start 2> /nfd.log"
  sleep 0.1
  docker exec relay$i-sidecar-1 nfdc cs config capacity 0
  docker exec -d relay$i-sidecar-1 nlsr -f /topology/relay$i-nlsr.conf
  docker exec -d relay$i-sidecar-1 sh -c "python3 /src/sidecar.py /relay$i"
  docker exec relay$i-sidecar-1 nlsrc advertise /relay$i
done

docker exec consumer sh -c "nfd-start 2> /nfd.log"
sleep 0.1
docker exec consumer nfdc cs config capacity 0
docker exec -d consumer nlsr -f /topology/consumer-nlsr.conf


# faces
docker exec producer nfdc face create tcp4://$HOST_IP:63601

for ((i=1; i<=$NUM_RELAIES; i++))
do
  PORT_PREV=$(printf "636%02d" $(($i-1)))
  PORT_NEXT=$(printf "636%02d" $(($i+1)))
  docker exec relay$i-sidecar-1 nfdc face create tcp4://$HOST_IP:$PORT_PREV
  docker exec relay$i-sidecar-1 nfdc face create tcp4://$HOST_IP:$PORT_NEXT
done
docker exec relay1-sidecar-1 nfdc face create tcp4://$HOST_IP:16363
docker exec relay$NUM_RELAIES-sidecar-1 nfdc face create tcp4://$HOST_IP:26363

docker exec consumer nfdc face create tcp4://$HOST_IP:$PORT
