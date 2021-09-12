import socket
import time
import sys


PS3MAPI_PORT        = 9671
PS3MAPI_BUF_SIZE    = 1024


class NotConnectedError(Exception):
    pass


class Ratchetron:
    ip = ""                         # type: str
    port = PS3MAPI_PORT             # type: int
    connected = False               # type: bool

    sock = None                     # type: socket.socket

    def __init__(self, ip: str):
        if len(ip.split(":")) > 1:  # support custom ps3mapi port numbers, probably never tested in practice
            self.port = int(ip.split(":")[1])
            ip = ip.split(":")[0]

        self.ip = ip

    def connect(self) -> bool:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))
        self.sock.settimeout(10.0)

        buf = bytearray(PS3MAPI_BUF_SIZE)
        n_bytes = 0
        try:
            n_bytes = self.sock.recv_into(buf, 6)
        except socket.timeout:
            print("timeout")

        if buf[0] != 1:
            return False

        self.connected = True

        return True

    def get_pid_list(self) -> [int]:
        self.sock.send(bytes([0x03]))

        buffer = bytearray(64)
        n_bytes = 0
        while n_bytes < 64:
            try:
                n_bytes += self.sock.recv_into(buffer, 64)
            except socket.timeout:
                print("timeout")

        pids = []
        for i in range(0, 63, 4):
            pids.append(int.from_bytes(buffer[i:i+4], "big"))

        return pids

    def notify(self, msg: str) -> str:
        buffer = [0x02]
        buffer += (len(msg)+1).to_bytes(4, "big")
        buffer += msg.encode('ascii')
        buffer += [0]

        self.sock.send(bytes(buffer))
        return "yo"

    def memory_set(self, pid: int, address: int, size: int, memory: bytearray):
        buffer = [0x05]
        buffer += pid.to_bytes(4, "big")
        buffer += address.to_bytes(4, "big")
        buffer += size.to_bytes(4, "big")
        buffer += memory

        self.sock.send(bytes(buffer))

    def memory_get(self, pid: int, address: int, size: int) -> bytearray:
        buffer = [0x04]
        buffer += pid.to_bytes(4, "big")
        buffer += address.to_bytes(4, "big")
        buffer += size.to_bytes(4, "big")

        self.sock.send(bytes(buffer))

        recv_buffer = bytearray(size)
        n_bytes = 0
        while n_bytes < size:
            try:
                n_bytes += self.sock.recv_into(recv_buffer, size)
            except socket.timeout:
                print("timeout")

        return recv_buffer

    def get_game_title_id(self) -> str:
        self.sock.send(bytes([0x06]))

        buffer = bytearray(16)
        n_bytes = 0
        while n_bytes < 16:
            try:
                n_bytes += self.sock.recv_into(buffer, 16)
            except socket.timeout:
                print("timeout")

        return buffer.decode('utf-8').rstrip("\x00")

    def get_game_title(self) -> str:
        self.sock.send(bytes([0x07]))

        buffer = bytearray(64)
        n_bytes = 0
        while n_bytes < 64:
            try:
                n_bytes += self.sock.recv_into(buffer, 64)
            except socket.timeout:
                print("timeout")

        return buffer.decode('utf-8').rstrip("\x00")

    def current_pid(self) -> int:
        return self.get_pid_list()[2]

if __name__ == "__main__":
    api = Ratchetron(sys.argv[1])
    if api.connect():
        print("Connected!")
        api.notify("Holy motherforking shirtballs!")
        api.notify("Can even send two notifications in a row, that's insane!")

        pid_list = api.get_pid_list()

        print(f"pids: {pid_list}")

        title_id = api.get_game_title_id()

        print(f"Game Title ID: {title_id}")
        print(f"Game Title: {api.get_game_title()}")

        if title_id == "NPEA00385":
            print("Ratchet & Clank 1 detected, showing bolt count in real time as demo.")
            while True:
                time.sleep(0.01666667)
                print("\rBolts: " + str(int.from_bytes(api.memory_get(pid_list[2], 0x00964a40, 4), "big")), end="")
    else:
        print("Couldn't connect!")