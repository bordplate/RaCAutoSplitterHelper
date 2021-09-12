import time
from Ratchetron import Ratchetron

ip = None

try:
    ip_file = open("ip.txt", "r")
    ip = ip_file.read()
    ip_file.close()
except FileNotFoundError:
    pass

if ip is None:
    print("IP: ", end="")
    ip = input()

    ip_file = open("ip.txt", "w")
    ip_file.write(ip)
    ip_file.close()

api = Ratchetron(ip)

if not api.connect():
    print(f"Error connecting to your system at IP {ip}. You can make sure Ratchetron is running by starting RaCMAN")
    exit(0)

pid = api.current_pid()

if pid == 0:
    print("Please start the game before starting AutoSplitter")
    exit(0)

title_id = api.get_game_title_id()

if title_id != "NPEA00385":
    print("This AutoSplitter currently only supports Ratchet & Clank 1 PAL")
    exit(0)

destination_planet_id = 0
planet_id = 0

while True:
    current_dest_planet_id = int.from_bytes(api.memory_get(pid, 0xa10704, 4), "big")
    current_planet_id = int.from_bytes(api.memory_get(pid, 0x969c70, 4), "big")
    if destination_planet_id != current_dest_planet_id and current_dest_planet_id != 0:
        destination_planet_id = current_dest_planet_id
        print(f"DESTINATION {destination_planet_id}")
    elif current_dest_planet_id == 0:
        destination_planet_id = 0

    if planet_id != current_planet_id:
        planet_id = current_planet_id
        print(f"PLANET {planet_id}")

    time.sleep(0.01666666667)