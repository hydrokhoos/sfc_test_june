import netifaces as ni

# Producer -- router1 -- router2 -...- routerN -- consumer
# 16363       63601      63602         636N       26363

PRODUCER = '16363'
CONSUMER = '26363'


class Node(object):
    def __init__(self, my_port: str, num_router: int) -> None:
        self.name = ''
        self.my_port = my_port
        self.num_router = num_router
        self.neighbors = []

        if self.my_port == PRODUCER:
            self.name = 'producer'
            self.neighbors.append('63601')
        if self.my_port == CONSUMER:
            self.name = 'consumer'
            self.neighbors.append('636' + str(num_router).zfill(2))
        if int(self.my_port[-2:]) == 1:
            self.neighbors.append(PRODUCER)
            if self.num_router > 1:
                self.neighbors.append('63602')
        if int(self.my_port[-2:]) == num_router:
            if self.num_router > 1:
                self.neighbors.append('636' + str(num_router-1).zfill(2))
            self.neighbors.append(CONSUMER)
        if not self.neighbors:
            prev = int(self.my_port[-2:]) - 1
            next = int(self.my_port[-2:]) + 1
            self.neighbors.append('636' + str(prev).zfill(2))
            self.neighbors.append('636' + str(next).zfill(2))

        if self.name == '':
            self.name = 'router' + self.my_port[-2:]

    def show(self):
        print(self.name.ljust(10), end='')
        print(self.my_port.ljust(10), end='')
        print(self.neighbors)


num_router = 3
routers_ports = ['636' + str(i).zfill(2) for i in range(1, num_router+1)]
producer = Node(PRODUCER, num_router)
consumer = Node(CONSUMER, num_router)
routers = []
for router in routers_ports:
    routers.append(Node(router, num_router))

print('name'.ljust(10), end='')
print('port'.ljust(10), end='')
print('neighbors')
producer.show()
for router in routers:
    router.show()
consumer.show()


TOPO_OUT_PATH = './created_topo/'
NETWORK = '/ndn'
SITE = '/test/'
ROUTER = '/%C1.Router/'
STATE_DIR = '/var/lib/nlsr'


for node in [producer]:
    general = 'general\n{\n'
    general += '  network ' + NETWORK + '\n'
    general += '  site ' + SITE + '\n'
    general += '  router ' + ROUTER + node.name + '\n'
    general += '  state-dir ' + STATE_DIR + '\n'
    general += '}\n'


print(general)
