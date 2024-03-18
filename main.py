import socket
import os
import qrcode
import time

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=15, border=2)

    qr.add_data(data)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save("./data/qr_code.png")
    print(data)

    print("QR Code generated successfully")

SERVER_HOST_NAME = socket.gethostname()
SERVER_HOST = socket.gethostbyname(SERVER_HOST_NAME) #"192.168.1.25"
print(SERVER_HOST)
SERVER_PORT = 5001

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"


def main():
    generate_qr_code((str(SERVER_HOST) + "," + str(SERVER_PORT)))
    s = socket.socket()

    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    client_socket, address = s.accept()
    print(f"[+] {address} is connected")

    #receive_file(client_socket)

    while True:
        received = client_socket.recv(BUFFER_SIZE).decode()
        print(received)
        
        title, exoselected = received.split(";")
        print(exoselected)

        client_socket.send("state;start".encode())

        # Start exo
        time.sleep(2)

        client_socket.send("state;finished".encode())
        


print("[*] Server closed")

main()