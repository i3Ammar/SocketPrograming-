import socket
import json
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.root = tk.Tk()
        self.root.title("Search in Dictionary ")

        self.create_widgets()

    def create_widgets(self):
        self.word_entry = ttk.Entry(self.root, width=30)
        self.word_entry.pack(pady=10)

        search_btn = ttk.Button(self.root, text="Search", command=self.start_search)
        search_btn.pack(pady=5)

        self.result_text = tk.Text(self.root, height=10, width=40)
        self.result_text.pack(pady=10)

    def search_word(self, word):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.send(json.dumps({'word': word}).encode())
                response = json.loads(s.recv(1024).decode())

                if 'meaning' in response:
                    return response['meaning']
                elif 'error' in response:
                    return f"Error: {response['error']}"
                else:
                    return "Invalid response from server"
        except (ConnectionRefusedError, TimeoutError):
            return "Error: Could not connect to server"
        except Exception as e:
            return f"Error: {str(e)}"

    def update_result(self, result):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

    def start_search(self):
        word = self.word_entry.get().strip()
        if not word:
            messagebox.showwarning("Input Error", "Please enter a word to search")
            return

        threading.Thread(target=self.threaded_search, args=(word,), daemon=True).start()

    def threaded_search(self, word):
        result = self.search_word(word)
        self.root.after(0, self.update_result, result)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = Client('localhost', 8080)
    client.run()