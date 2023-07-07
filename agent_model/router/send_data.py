import socket
import base64
import time

BUFFER_SIZE = 512 * 1024


def send_data(dest_ip, dest_port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((dest_ip, dest_port))
        encoded_data = base64.b64encode(data)
        s.sendall(encoded_data)

        s.shutdown(socket.SHUT_WR)

        recv_data = b''
        while True:
            chunk = s.recv(BUFFER_SIZE)
            if not chunk:
                break
            recv_data += chunk

        return base64.b64decode(recv_data)


if __name__ == '__main__':
    # data = b'hello'
    # print('sending:', data)
    # result = send_data('localhost', 8888, data)
    # print('received:', result)
    with open('/src/gray-blur-santa_monica.jpg', 'rb') as f:
        # with open('/src/santa_monica.jpg', 'rb') as f:
        data = f.read()
        print(len(data))
    processed = send_data('blur', 1234, data)
    print(len(processed))
