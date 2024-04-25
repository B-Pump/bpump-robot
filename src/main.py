from flask import Flask
from flask_socketio import SocketIO
from pyngrok import ngrok

from codeqr import QRCode
from exercice import Exercice

app = Flask(__name__, static_folder="videos", static_url_path="/videos")
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")

def start_exercice(data, metabolism):
    exercice = Exercice()

    exercice.start_proj(data)
    exercice.start_cam(socketio, data, metabolism, False)

@socketio.event
def connect():
    print("[+] Connected")

@socketio.event
def disconnect():
    print("[-] Disconnected")

@socketio.event
def start_exo(data):
    data["data"]["reps"] = 12
    data["data"]["rest"] = 0

    start_exercice(data["data"], data["metabolism"])

@socketio.event
def start_program(data):
    for exo in data["data"]:
        start_exercice(exo, data["metabolism"])

if __name__ == "__main__":
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5001 

    ngrok_tunnel = ngrok.connect(addr=f"{SERVER_HOST}:{SERVER_PORT}", bind_tls=True)
    print(f"ngrok tunnel created : {ngrok_tunnel.public_url}") # debug purposes

    QRCode().generate(ngrok_tunnel.public_url)
    socketio.run(app, host=SERVER_HOST, port=SERVER_PORT)