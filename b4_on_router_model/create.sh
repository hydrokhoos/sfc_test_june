#!/bin/bash

HOST_IP=$(ipconfig getifaddr en0)

# start containers
docker run -dit --name producer --privileged -p $HOST_IP:16363:6363 --cpuset-cpus=3 hydrokhoos/ndn-all:arm
sed -e "s/<ip>/$HOST_IP/g" ./topology/producer-nlsr.conf > nlsr.conf
docker cp nlsr.conf producer:/nlsr.conf
docker cp ../nfd-router.conf producer:/nfd.conf
docker cp ../img.jpg producer:/img.jpg

docker run -dit --name consumer --privileged -p $HOST_IP:26363:6363 --cpuset-cpus=4 hydrokhoos/ndn-all:arm
sed -e "s/<ip>/$HOST_IP/g" ./topology/consumer-nlsr.conf > nlsr.conf
docker cp nlsr.conf consumer:/nlsr.conf
docker cp ../nfd-router.conf consumer:/nfd.conf

docker run -dit --name router1 --privileged -p $HOST_IP:63601:6363 --cpuset-cpus=5 hydrokhoos/ndn-all:arm
sed -e "s/<ip>/$HOST_IP/g" ./topology/router1-nlsr.conf > nlsr.conf
docker cp nlsr.conf router1:/nlsr.conf
docker cp ../nfd-router.conf router1:/nfd.conf

rm nlsr.conf


# start NFD & NLSR
docker exec producer sh -c "ndnsec key-gen /producer | ndnsec cert-install -"
docker exec -d producer sh -c "nfd -c nfd.conf 2> /nfd.log"
sleep 0.1
docker exec -d producer sh -c "nlsr -f /nlsr.conf"
docker exec producer nlsrc advertise /img.jpg
docker exec -d producer sh -c "ndnputchunks /img.jpg < /img.jpg"

docker exec consumer sh -c "ndnsec key-gen /consumer | ndnsec cert-install -"
docker exec -d consumer sh -c "nfd -c nfd.conf 2> /nfd.log"
sleep 0.1
docker exec -d consumer sh -c "nlsr -f /nlsr.conf"

docker exec router1 sh -c "ndnsec key-gen /router1 | ndnsec cert-install -"
docker exec -d router1 sh -c "nfd -c nfd.conf 2> /nfd.log"
sleep 0.1
docker exec -d router1 sh -c "nlsr -f /nlsr.conf"

# create faces
docker exec producer sh -c "nfdc face create tcp4://$HOST_IP:63601"

docker exec consumer sh -c "nfdc face create tcp4://$HOST_IP:63601"

docker exec router1 sh -c "nfdc face create tcp4://$HOST_IP:16363"
docker exec router1 sh -c "nfdc face create tcp4://$HOST_IP:26363"
