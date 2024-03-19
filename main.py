import socket
import os
import qrcode
import time

from lib.qrcode import QRCode

SERVER_HOST_NAME = socket.gethostname()
SERVER_HOST = socket.gethostbyname(SERVER_HOST_NAME) #"192.168.1.25"
SERVER_PORT = 5001
BUFFER_SIZE = 4096

def main():
    qr = QRCode()

    while True:
        try:
            print(f"[*] Server is Starting")
            s = socket.socket()
            
            print(f"[*] Generating QRCode!")
            qr.generate((str(SERVER_HOST) + "," + str(SERVER_PORT)))

            s.bind((SERVER_HOST, SERVER_PORT))
            s.listen(5)
            print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

            client_socket, address = s.accept()
            print(f"[+] {address} is connected")

            while True:
                received = client_socket.recv(BUFFER_SIZE).decode()
                print(received)
                
                title, message = received.split(";")
                print(f"{title} : {message}")

                client_socket.send("state;start".encode())

                # TODO: start exo

                time.sleep(2)

                client_socket.send("state;finished".encode())
        except:
            print(f"[*] Server has encounter an error!")
            print(f"[*] Server will restart!")
        
        print(f"[*] Server closed")
main()