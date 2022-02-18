import json
import threading


class ClientThread(threading.Thread):
    client_address = None
    client_socket = None
    serial_object = None

    def __init__(self, client_address, client_socket, serial_object):
        self.serial_object = serial_object
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        print("New connection added: ", self.client_address)

    def run(self):
        print("Connection from : ", self.client_address)
        self.client_socket.send(bytes("Hi, This is from Server..", 'utf-8'))
        while True:
            try:
                data = self.client_socket.recv(2048)
                msg = data.decode()
                if msg == 'bye':
                    break
                # print("from client", msg)
                if msg == "connect":
                    json_ = json.dumps({"last_data": self.serial_object.serial_thread.last_data})
                    self.client_socket.send(bytes(json_, 'UTF-8'))
                if len(msg) == 0:
                    break
            except ConnectionResetError:
                break
        print("Client at ", self.client_address, " disconnected...")
