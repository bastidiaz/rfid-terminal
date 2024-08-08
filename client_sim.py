# Make sure to run the server first before running this script.
# Also, I suggest making 2-3 variations of this script to simulate
# multiple clients with different location IDs and deduction matrices.

import socket
import json
import time
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8000

LOCATION_ID = "CDM"
DEDUCTION_MATRIX = {
    "EMD": 50,
    "NMD": 30,
    "SMD": 45
}

RFID_LIST = [
    "9D1562F5", "0EFE2007", "07B70C5F",
    "3FEBB4C2", "2B16E64D", "419277B4",
    "4B7AAE7D", "E06E52D9", "5A11353D",
    "8E78ADDD", "85D88382", "8A9C5025",
    "70711922", "53725766", "C37AE534"
]

rfid_iterator = iter(RFID_LIST)


def get_next_rfid():
    global rfid_iterator
    try:
        return next(rfid_iterator)
    except StopIteration:
        # Reset the iterator if the end of the list is reached
        rfid_iterator = iter(RFID_LIST)
        return next(rfid_iterator)


def send_to_server(rfid_data):
    payload = {
        "rfid_data": rfid_data,
        "location_id": LOCATION_ID,
        "deduction_matrix": DEDUCTION_MATRIX
    }
    payload_json = json.dumps(payload)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            client_socket.sendall(payload_json.encode('utf-8'))

            response = client_socket.recv(4096).decode('utf-8')
            print(f"Server response for RFID {rfid_data}: {response}")
    except Exception as e:
        print(f"An error occurred for RFID {rfid_data}: {e}")


def worker():
    while True:
        rfid_data = get_next_rfid()
        send_to_server(rfid_data)
        time.sleep(3)


num_threads = 3
threads = []

for _ in range(num_threads):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

