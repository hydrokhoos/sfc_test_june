BASE_TOPO_PATH=../topology_base/topo_1/
OUT_TOPO_PATH=./topology_2/

HOST_IP=$(ipconfig getifaddr en0)

for conf in `ls $BASE_TOPO_PATH`
do
  echo $conf
  sed -e "s/<ip>/$HOST_IP/g" $BASE_TOPO_PATH$conf > $OUT_TOPO_PATH$conf
done
