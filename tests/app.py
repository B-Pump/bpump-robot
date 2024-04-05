import sys
import socketio

sys.path.append('../bpump-robot')

from lib.codeqr import QRCode
qr = QRCode()

sio = socketio.Client()

BUFFER_SIZE = 4096

@sio.event
def connect():
    print("[+] Connected")

@sio.event
def disconnect():
    print("[-] Disconnected")

if __name__ == "__main__":
    host, port = qr.read("./output/qr_code.jpg").split(":", 2)

    print(f"[+] Connecting to {host}:{port}")
    sio.connect(f"http://{host}:{port}")

    while True:
        exoselected = str(input(f"Which exercise do you want to do ?\n\n1 - Curl\n2 - Squats\n3 - Pushups\n\n            exo rep\n Response : "))
        
        sio.emit("message", {"data": f"start;{exoselected}"})

        @sio.on("message")
        def handle_message(data):
            print(f"Received data : {data}") 
            title, response = data["data"].split(";")
            
            if title == "start":
                print(response)
            elif title == "finished":
                print(response)
            else:
                print(response)

#sio.disconnect()