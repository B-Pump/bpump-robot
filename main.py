import socket

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

@sio.event
def start_exo(sid, data):
    print(data["data"]["title"])

if __name__ == "__main__":
    SERVER_HOST_NAME = socket.gethostname()
    SERVER_HOST = socket.gethostbyname(SERVER_HOST_NAME)
    SERVER_PORT = 5001

    ngrok_tunnel = ngrok.connect(addr=f"{SERVER_HOST}:{SERVER_PORT}", bind_tls=True)
    print(f"ngrok tunnel created : {ngrok_tunnel.public_url}")

    qr.generate(ngrok_tunnel.public_url)
    eventlet.wsgi.server(eventlet.listen((SERVER_HOST, SERVER_PORT)), app)