import socket
import os
from pyzbar.pyzbar import decode
from PIL import Image
import os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

def read_qr_code(path):
    if os.path.exists(path):
        for obj in decode(Image.open(path)):
            print("Decoded QR Code:", obj.data.decode("utf-8"))
            return obj.data.decode("utf-8")
    else:
        print("Image not found")


with socket.socket() as s:
    host, port = read_qr_code("./data/qr_code.png").split(",", 2)
    print(host)
    print(port)

    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, int(port)))
    print("[+] Connected")

    while True:
        exoselected = str(input(f"""{"="*40}
Which exercise do you want to do?
    1 - Curl
    2 - Squats
    3 - Pushups
{"="*40}
Response: """))
        
        s.send(f"start;{exoselected}".encode())
        
        while True:
            received = s.recv(BUFFER_SIZE).decode()
            title, response = received.split(";")
            if response == "start":
                print("Exo start!")
            elif response == "finished":
                print("Exo finished!")
                break
            else:
                print(response)
