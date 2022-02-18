import os.path
import logging
import serial
import threading
import time
import socket

from io import BytesIO
from wyl.client_thread import ClientThread
from wyl.config import Config
from wyl.helpers import StoppableThread


logging.basicConfig(
    filename=os.path.join("logs", "last_data.log"),
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s|%(levelname)s|%(message)s'
)


def log(msg, type=None):
    types_ = ["debug", "info", "warning", "error"]
    if type is None:
        logging.info(msg)
    else:
        if type in types_:
            if type == "debug":
                logging.debug(msg)
            if type == "info":
                logging.debug(msg)
            if type == "error":
                logging.error(msg)
            if type == "warning":
                logging.warning(msg)


class Serial(object):
    serial_thread = None

    class SerialThread(StoppableThread):
        _serial = None
        b = None
        s = None
        running = True
        last_data_t = None
        last_data = []

        def __init__(self, com_port, serial_baudrate=None, timeout=None):
            self._serial = serial.Serial(
                com_port,
                baudrate=serial_baudrate,
                timeout=0 if timeout is None else timeout
            )
            self.b = bytes()
            self.b_ = BytesIO(self.b)
            super(Serial.SerialThread, self).__init__()
            self._stop_event = threading.Event()

        def run(self) -> None:
            while not self.stopped():
                while self.running:
                    self.s = self._serial.read()
                    if len(self.s) > 0:
                        self.last_data_t = time.time()
                        if self.s.decode("utf-8") == "\n":
                            str_ = self.b.decode("utf-8").rstrip("\r")
                            if len(str_) > 0:
                                if len(self.last_data) >= 20:
                                    self.last_data.pop(0)
                                if not os.path.isdir("logs"):
                                    os.mkdir("logs")

                                log(str_)
                                self.last_data.append({"t": self.last_data_t, "str": str_})

                                if self.stopped():
                                    self.running = False
                                    break
                                    break
                            self.b = bytes()
                        else:
                            self.b += self.s

    def stop_serial(self):
        self.serial_thread.stop()
        self.serial_thread.running = False

    def start_serial(self, com_port, baudrate):
        self.serial_thread = Serial.SerialThread(com_port, baudrate)
        self.serial_thread.start()

    @staticmethod
    def start_sock():
        global config
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((config.HOST, config.PORT))
        return s


config = None

if __name__ == '__main__':
    config = Config()

    server = Serial.start_sock()
    serial_ = Serial()
    serial_.start_serial(config.COM_PORT, config.BAUDRATE)

    count = 0
    try:
        while True:
            server.listen(1)
            client_sock, client_address = server.accept()
            newthread = ClientThread(client_address, client_sock, serial_)
            newthread.start()
            time.sleep(1)
    except KeyboardInterrupt:
        serial_.stop_serial()
        pass
