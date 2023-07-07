import socket
import base64
import urllib.request
import json
import time

import app


RECEIVE_SIZE = 512 * 1024


def register_service(router_url, service_name, service_ip, service_port):
    headers = {"Content-Type": "application/json"}

    obj = {
        "service_name": service_name,
        "service_ip": service_ip,
        "service_port": service_port
    }
    json_data = json.dumps(obj).encode('utf-8')
    request = urllib.request.Request(
        router_url, data=json_data, method="POST", headers=headers
    )
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode('utf-8')


def unregister_service(router_url, service_name):
    headers = {"Content-Type": "application/json"}

    obj = {"service_name": service_name}
    json_data = json.dumps(obj).encode('utf-8')
    request = urllib.request.Request(
        router_url, data=json_data, method="DELETE", headers=headers
    )
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode('utf-8')


def process_data(data):
    return app.function(data)


def serve(service_ip, service_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((service_ip, service_port))
        s.listen()

        while True:
            client_sock, client_address = s.accept()

            recv_data = b''
            while True:
                _data = client_sock.recv(RECEIVE_SIZE)

                if not _data:
                    break
                else:
                    recv_data += _data
            print('received data size: ', len(recv_data))
            recv_data = base64.b64decode(recv_data)
            t = time.time()
            processed_data = process_data(recv_data)
            print('service time: ', time.time() - t)
            print('processed data size: ', len(processed_data))
            print()
            response_data = base64.b64encode(processed_data)

            client_sock.sendall(response_data)
            client_sock.close()


if __name__ == '__main__':
    import os
    router_url = "http://"+os.environ['HOST_IP']+":8888"
    # service_name = '/relay'
    # service_ip = 'relay1'
    service_name = os.environ['SERVICE_NAME']
    service_ip = os.environ['SERVICE_NAME']
    service_port = 1234

    print('register service')
    register_service(router_url + "/put_service",
                     service_name, service_ip, service_port)

    print('start service')
    try:
        serve(service_ip, service_port)
    finally:
        print('unregister service')
        unregister_service(router_url + "/del_service", service_name)
