import socket, threading

import eventlet, socketio
from pyngrok import ngrok

from lib.codeqr import QRCode
from lib.exercice import Exercice 

qr = QRCode()
exercice = Exercice()

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f"[+] Connected : {sid}")

@sio.event
def disconnect(sid):
    print(f"[-] Disconnected : {sid}")

@sio.event
def message(sid, data):
    print(f"[*] Received data : {data}")

def start_exo_thread(data):
    exercice_data = data["data"]
    exercice.start_proj(exercice_data)
    exercice.start_cam(exercice_data, 4)

@sio.event
def start_exo(sid, data):
    threading.Thread(target=start_exo_thread, args=(data,)).start()

def send_stats(data):
    sio.emit("result", data)

if __name__ == "__main__":
    SERVER_HOST = socket.gethostbyname(socket.gethostname())
    SERVER_PORT = 5001

    ngrok_tunnel = ngrok.connect(addr=f"{SERVER_HOST}:{SERVER_PORT}", bind_tls=True)
    print(f"ngrok tunnel created : {ngrok_tunnel.public_url}")

    qr.generate(ngrok_tunnel.public_url)
    eventlet.wsgi.server(eventlet.listen((SERVER_HOST, SERVER_PORT)), app)