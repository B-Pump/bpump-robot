from socket import gethostbyname, gethostname
from os import devnull

from eventlet import listen, wsgi
from socketio import Server, WSGIApp
from pyngrok import ngrok

from codeqr import QRCode
from exercice import Exercice

sio = Server(cors_allowed_origins="*")
app = WSGIApp(sio)

def start_exercice(data, metabolism):
    exercice = Exercice()

    exercice.start_proj(sio, data)
    exercice.start_cam(sio, data, 5, metabolism, False)

@sio.event
def connect(sid, environ):
    print(f"[+] Connected : {sid}")

@sio.event
def disconnect(sid):
    print(f"[-] Disconnected : {sid}")

@sio.event
def start_exo(sid, data):
    start_exercice(data["data"], data["metabolism"])

@sio.event
def start_program(sid, data):
    for exo in data["data"]:
        start_exercice(exo, data["metabolism"])

if __name__ == "__main__":
    SERVER_HOST = gethostbyname(gethostname())
    SERVER_PORT = 5001

    ngrok_tunnel = ngrok.connect(addr=f"{SERVER_HOST}:{SERVER_PORT}", bind_tls=True)
    # print(f"ngrok tunnel created : {ngrok_tunnel.public_url}")

    QRCode().generate(ngrok_tunnel.public_url)
    wsgi.server(listen((SERVER_HOST, SERVER_PORT)), app, log=open(devnull, "w"))