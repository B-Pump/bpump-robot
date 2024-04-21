import socket

import eventlet, socketio
from pyngrok import ngrok

from codeqr import QRCode

from exercice import Exercice

qr = QRCode()


sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

def start_exercice(sid, data, metabolism):
    exercice = Exercice()
    # exercice.start_proj(data)
    exercice.start_cam(data, 5, metabolism)

@sio.event
def connect(sid, environ):
    print(f"[+] Connected : {sid}")

@sio.event
def disconnect(sid):
    print(f"[-] Disconnected : {sid}")

@sio.event
def start_exo(sid, data):
    start_exercice(sid, data["data"], data["metabolism"])

@sio.event
def start_program(sid, program):
    print(program["metabolism"])
    metabolism = program["metabolism"]
    for exo in program["data"]:
        start_exercice(sid, exo, metabolism)

def send_stats(data):
    sio.emit("result", data)

if __name__ == "__main__":
    SERVER_HOST = socket.gethostbyname(socket.gethostname())
    SERVER_PORT = 5001

    ngrok_tunnel = ngrok.connect(addr=f"{SERVER_HOST}:{SERVER_PORT}", bind_tls=True)
    print(f"ngrok tunnel created : {ngrok_tunnel.public_url}")

    qr.generate(ngrok_tunnel.public_url)
    eventlet.wsgi.server(eventlet.listen((SERVER_HOST, SERVER_PORT)), app)