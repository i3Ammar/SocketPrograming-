import socket
import json
import argparse
from concurrent.futures import ThreadPoolExecutor

class Server:
    def __init__(self, host, port, dict_file):
        self.host = host
        self.port = port
        self.dictionary = self.load_dictionary(dict_file)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.pool = ThreadPoolExecutor(max_workers=10)

    @staticmethod
    def load_dictionary( file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading dictionary: {e}")
            exit(1)

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break

                try:
                    request = json.loads(data)
                    word = request.get('word', '')
                    response = {'meaning': self.dictionary.get(word, '')}
                    if not response['meaning']:
                        response = {'error': 'Word not found'}
                except json.JSONDecodeError:
                    response = {'error': 'Invalid request format'}

                client_socket.send(json.dumps(response).encode())
        except ConnectionResetError:
            pass
        finally:
            client_socket.close()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"Accepted connection from {addr}")
                self.pool.submit(self.handle_client, client_socket)
        except KeyboardInterrupt:
            print("Shutting down server...")
        finally:
            self.server_socket.close()
            self.pool.shutdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dictionary Server')
    parser.add_argument('port', type=int, help='Port number')
    parser.add_argument('dict_file', help='Path to dictionary file')
    args = parser.parse_args()

    server = Server('localhost', args.port, args.dict_file)
    server.start()
