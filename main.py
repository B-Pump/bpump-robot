import socket
import time

from lib.codeqr import QRCode
from lib.exercice import Exercice

def main():
    SERVER_HOST_NAME = socket.gethostname()
    SERVER_HOST = socket.gethostbyname(SERVER_HOST_NAME)
    SERVER_PORT = 5001
    BUFFER_SIZE = 4096

    qr = QRCode()
    exercice = Exercice()

    while True:
        try:
            print(f"[*] Server is Starting")
            s = socket.socket()
            
            print(f"[*] Generating QRCode!")
            qr.generate((str(SERVER_HOST) + ":" + str(SERVER_PORT)))

            s.bind((SERVER_HOST, SERVER_PORT))
            s.listen(5)
            print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

            client_socket, address = s.accept()
            print(f"[+] {address} is connected")

            while True:
                received = client_socket.recv(BUFFER_SIZE).decode()
                print(f"Received data : {received}")
                
                title, message = received.split(";")
                
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
                        client_socket.send(("start;exo:"+todo).encode())

                    def start_cam(todo, rep):
                        exercice.start_cam(todo, reps)
                        client_socket.send(("start;exo:"+todo+",rep:"+str(reps)).encode())

                    start_projector(todo)
                else:
                    client_socket.send("error;Vous avez mal répondu au formulaire".encode())

                # TODO: start exo

                time.sleep(1)

                client_socket.send(("finished;exo:" + todo + ",rep:" + str(reps)).encode())
        except:
            print(f"[*] Server has encounter an error !")
            print(f"[*] Server will restart !")
        
        print(f"[*] Server closed")

if __name__ == "__main__":
    main()