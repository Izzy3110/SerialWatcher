import json
import socket
import time

SERVER = "127.0.0.1"
PORT = 8001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes("This is from Client", 'UTF-8'))

while True:
    try:
        in_data = client.recv(4096)
        json_str = in_data.decode("utf-8")
        try:
            json_ = json.loads(json_str)
            json_c = {
              "count": len(json_["last_data"]),
              "last": json_["last_data"][len(json_["last_data"])-1]
            }
            print(json.dumps(json_c, indent=4))

        except json.decoder.JSONDecodeError:
            print("no json: ")
            print(json_str)
        except IndexError:
            pass
        client.sendall(bytes("connect", 'UTF-8'))

    except ConnectionResetError:
        print("connection lost... reconnecting")
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER, PORT))
        except OSError:
            pass
        pass

    except OSError:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER, PORT))
        except OSError:
            pass
        pass
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        pass
client.close()
