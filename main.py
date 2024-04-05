import eventlet
import socketio
import time
import socket

from lib.codeqr import QRCode
qr = QRCode()

from lib.exercice import Exercice
exercice = Exercice()

sio = socketio.Server()
app = socketio.WSGIApp(sio)


@ sio.event
def connect(sid, environ):
    print(f"[*] {sid} connected")

@ sio.event
def disconnect(sid):
    print(f"[*] {sid} disconnected")

@ sio.event
def message(sid, data):
    print(f"Received data : {data}")    # {'data': 'start;1 2'}
    title, message = data["data"].split(";")

    todo = ""

    exo, reps = message.split(" ")
    reps = int(reps)

    if exo and reps:
        if exo == "1":
            todo = "pullup"
        elif exo == "2":
            todo = "curl"
        elif exo == "3":
            todo = "pushup"
        elif exo == "4":
            todo = "situp"
        elif exo == "5":
            todo = "squat"

        def start_projector(todo):
            exercice.start_proj(todo)
            sio.emit("message", {"data": "start;exo:"+todo}, room=sid)

        def start_cam(todo, rep):
            exercice.start_cam(todo, reps)
            sio.emit("message", {"data": "start;exo:"+todo+",rep:"+str(reps)}, room=sid)

        start_projector(todo)
    else:
        sio.emit("message", {"data": "error;Vous avez mal répondu au formulaire"}, room=sid)

    # TODO: start exo

    time.sleep(1)

    sio.emit("message", {"data": "finished;exo:" + todo + ",rep:" + str(reps)}, room=sid)

if __name__ == "__main__":
    SERVER_HOST_NAME = socket.gethostname()
    SERVER_HOST = socket.gethostbyname(SERVER_HOST_NAME)
    SERVER_PORT = 5001

    print(f"[*] Server is starting")
    qr.generate(f"{SERVER_HOST}:{SERVER_PORT}")

    eventlet.wsgi.server(eventlet.listen((SERVER_HOST, SERVER_PORT)), app)
