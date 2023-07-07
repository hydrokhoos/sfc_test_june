ndnsec key-gen $1 | ndnsec cert-install -
nlsrc -R $ROUTER_PREFIX -k advertise $1
python3 /src/sidecar.py $1
