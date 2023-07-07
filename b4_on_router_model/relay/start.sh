ndnsec key-gen $1 | ndnsec cert-install -
nfd -c /src/nfd.conf 2> /nfd.log &
python3 /src/sidecar.py $1
