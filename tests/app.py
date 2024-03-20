import socket

from lib.qrcode import QRCode

BUFFER_SIZE = 4096


with socket.socket() as s:
    host, port = QRCode.read("./data/qr_code.jpg").split(",", 2)
    print(host)
    print(port)

    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, int(port)))
    print("[+] Connected")

    while True:
        exoselected = str(input(f"Which exercise do you want to do ?\n\n1 - Curl\n2 - Squats\n3 - Pushups\n\nResponse : "))
        
        s.send(f"start;{exoselected}".encode())
        
        while True:
            received = s.recv(BUFFER_SIZE).decode()
            title, response = received.split(";")
            if response == "start":
                print("Exo start !")
            elif response == "finished":
                print("Exo finished !")
                break
            else:
                print(response)