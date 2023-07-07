import os
import sys
import shutil
import netifaces as ni


num_service = int(sys.argv[1])

dir_base = "./relay"
dirs = [dir_base + str(i) for i in range(1, num_service + 1)]

for i, dir in enumerate(dirs):
    ip = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']
    port = '636{:02}'.format(i + 1)
    shutil.copytree(dir_base, dir, dirs_exist_ok=True)
    with open(os.path.join(dir, "docker-compose.yaml"), "r") as f:
        yaml = f.read()
        yaml = yaml.replace('<ip:port>', ':'.join((ip, port)))
        yaml = yaml.replace('<service_name>', f'relay{i + 1}')
        yaml = yaml.replace('<service_id>', f'\'{i + 1}\'', )
    with open(os.path.join(dir, "docker-compose.yaml"), "w") as f:
        f.write(yaml)


dir_topology = './topology'

shutil.copytree('../topology_base/topo_'+str(num_service),
                dir_topology, dirs_exist_ok=True)

with open(os.path.join(dir_topology, 'producer-nlsr.conf'), 'r') as f:
    nlsr = f.read()
with open(os.path.join(dir_topology, 'producer-nlsr.conf'), 'w') as f:
    f.write(nlsr.replace('<ip>', ip))
with open(os.path.join(dir_topology, 'consumer-nlsr.conf'), 'r') as f:
    nlsr = f.read()
with open(os.path.join(dir_topology, 'consumer-nlsr.conf'), 'w') as f:
    f.write(nlsr.replace('<ip>', ip))

nlsr_files = [os.path.join(
    dir_topology, f'relay{i+1}-nlsr.conf') for i in range(num_service)]
for nlsr_file in nlsr_files:
    with open(nlsr_file, 'r') as f:
        nlsr = f.read()
    with open(nlsr_file, 'w') as f:
        f.write(nlsr.replace('<ip>', ip))
