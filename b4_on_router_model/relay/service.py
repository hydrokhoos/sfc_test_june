import app
import importlib
import json
import socket
import time
import os

import sys
sys.dont_write_bytecode = True


SIDECAR_IP = 'sidecar'
SERVICE_IP = 'service'
PORT = 1234
BUFFER_SIZE = 1024
DATA_VOLUME_PATH = '/data/'


def listen_single_msg():
    print('listening')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((SERVICE_IP, PORT))
        s.listen()

        # recieve from sidecar
        while True:
            received_message = b''
            client_sock, client_address = s.accept()

            # LISTENING TO SIDECAR
            while True:
                chunk = client_sock.recv(BUFFER_SIZE)

                if not chunk:
                    break
                else:
                    received_message += chunk
            print(received_message.decode())
            received_json = json.loads(received_message.decode())

            # READ DATA ON VOLUME
            data = b''
            data_path = os.path.join(
                DATA_VOLUME_PATH, received_json['filename'])
            with open(data_path, 'rb') as f:
                data = f.read()

            # CALL SERVICE FUNCTION
            print('call service function')
            importlib.reload(app)
            t = time.time()
            processed_data = app.function(data)
            print('service time:'.ljust(20), time.time() - t)

            # WRITE PROCESSED DATA ON VOLUME
            processd_data_name = 'processed-' + received_json['filename']
            with open(os.path.join(DATA_VOLUME_PATH, processd_data_name), 'wb') as f:
                f.write(processed_data)

            # SEND MSG TO SIDECAR
            send_message = json.dumps(
                {'filename': processd_data_name}).encode()
            client_sock.sendall(send_message)
            client_sock.close()


if __name__ == '__main__':
    listen_single_msg()
