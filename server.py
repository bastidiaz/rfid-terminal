import socket
import os
import json
import logging
from multiprocessing import Process, Lock


DB_FOLDER = 'db'
HOST = '127.0.0.1'
PORT = 8000

file_lock = Lock()


logging.basicConfig(
        filename = 'server_log.txt',
        level = logging.INFO,
        format = '%(asctime)s - %(levelname)s - %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S'
        )

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024).decode('utf-8').strip()
        # print(f"Received data: {data}")  # Debug statement
        logging.info(f"Received data: {data}")
        if data:
            data_json = json.loads(data)
            rfid_data = data_json.get('rfid_data')
            location_id = data_json.get('location_id')
            deduction_matrix = data_json.get('deduction_matrix', {})

            if not rfid_data or not location_id:
                client_socket.sendall(b"Invalid data received")
                logging.warning("Invalid data received")
                return

            file_name = f"{rfid_data}.txt"
            file_path = os.path.join(DB_FOLDER, file_name)
            response = process_data(file_path, location_id, deduction_matrix)

            try:
                with open(file_path, 'r') as file:
                    contents = file.read()
                    client_socket.sendall(response.encode('utf-8') + b"\n" + contents.encode('utf-8'))
                logging.info(f"Response sent: {response}")
            
            except FileNotFoundError:
                client_socket.sendall(response.encode('utf-8'))
                logging.error(f"Response sent: {response}")

        else:
            client_socket.sendall(b"Invalid data received")
            logging.warning("No data received")
    except Exception as e:
        # print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")
    finally:
        client_socket.close()


def process_data(file_path, location_id, deduction_matrix):
    try:
        if not os.path.exists(DB_FOLDER):
            os.makedirs(DB_FOLDER)
            logging.info(f"Created directory: {DB_FOLDER}")

        with file_lock:
            if not os.path.isfile(file_path):
                logging.warning("Invalid card!")
                return "Invalid card detected. Use a valid card next time or you may be apprehended."

            with open(file_path, 'r+') as file:
                lines = file.readlines()
                balance = 0
                current_origin = ""
                origin_line_index = balance_line_index = -1

                for index, line in enumerate(lines):
                    if line.startswith("Origin"):
                        origin_line_index = index
                        current_origin = line.split('\t')[1].strip()
                    elif line.startswith("Balance"):
                        balance_line_index = index
                        balance = int(line.split('\t')[1])

                if current_origin == location_id:
                    response = update_location(lines, origin_line_index, None)
                elif current_origin in deduction_matrix:
                    response = update_balance(lines, balance_line_index, origin_line_index, balance, current_origin,
                                              location_id, deduction_matrix)
                else:
                    response = update_location(lines, origin_line_index, location_id)

                file.seek(0)
                file.writelines(lines)
                file.truncate()

                logging.info(f"Updated file: {file_path} with response: {response}")
                return response

    except Exception as e:
        print(f"An error occurred while updating the file: {e}")


def update_location(lines, origin_line_index, new_location):
    if new_location:
        lines[origin_line_index] = f"Origin\t{new_location}\n"
        return f"Entry point set to {new_location}. Have a safe trip!"
    else:
        lines[origin_line_index] = "Origin\t\n"
        return "No deductions for same district exits."


def update_balance(lines, balance_line_index, origin_line_index, balance, current_origin, location_id,
                   deduction_matrix):
    deduction_amount_cents = deduction_matrix[current_origin]
    if balance < deduction_amount_cents:
        return "Insufficient balance. Top-up with a tollbooth to exit!"

    balance -= deduction_amount_cents
    lines[balance_line_index] = f"Balance\t{balance}\n"
    lines[origin_line_index] = "Origin\t\n"
    return f"Deducted Php{deduction_amount_cents} from the balance. Welcome to {location_id}!"


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    logging.info(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server.accept()
            logging.info(f"Accepted connection from {addr}")
            client_handler = Process(target=handle_client, args=(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
    finally:
        server.close()


if __name__ == "__main__":
    main()
