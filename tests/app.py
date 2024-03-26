import sys

import socket

sys.path.append('../bpump-robot')

from lib.codeqr import QRCode

BUFFER_SIZE = 4096

with socket.socket() as s:
    host, port = QRCode().read("./output/qr_code.jpg").split(":", 2)

    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, int(port)))
    print("[+] Connected")

    while True:
        exoselected = str(input(f"Which exercise do you want to do ?\n\n1 - Curl\n2 - Squats\n3 - Pushups\n\n            exo rep\n Response : "))
        
        s.send(f"start;{exoselected}".encode())
        
        while True:
            received = s.recv(BUFFER_SIZE).decode()
            title, response = received.split(";")
            
            if title == "start":
                print(response)
            elif title == "finished":
                print(response)
                break
            else:
                print(response)