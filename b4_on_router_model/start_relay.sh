HOST_IP=$(ipconfig getifaddr en0)

if test "$1" = ""; then
  echo "missing relay number"
  echo "Usage: $0 <relay_number>"
  exit 1
fi

cp -r relay relay$1
sed -e "s/<ip>/$HOST_IP/g" -e "s/<port>/3636$1/g" -e "s/<service_name>/relay$1/g" -e "s/<service_id>/'$i'/g" relay/docker-compose.yaml > relay$1/docker-compose.yaml

cp ../nfd-router.conf relay$1/nfd.conf

cd ./relay$1/ && docker-compose up -d && cd ..
sleep 0.1
docker exec router1 nfdc face create tcp4://$HOST_IP:3636$1
docker exec router1 nfdc route add /relay$1 nexthop tcp4://$HOST_IP:3636$1
docker exec router1 sh -c "nlsrc advertise /relay$1"
docker exec relay$1-sidecar-1 nfdc face create tcp4://$HOST_IP:63601
docker exec relay$1-sidecar-1 nfdc route add / nexthop tcp4://$HOST_IP:63601
