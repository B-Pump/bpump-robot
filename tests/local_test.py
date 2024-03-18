import threading
from lib.exercie import Exercices
exercices = Exercices()

user_input = str(input(f"""{"="*40}
Which exercise do you want to do?
    1 - Curl
    2 - Squats
    3 - Pushups
{"="*40}
Response: """))

rep = int(input("How many rep: "))

exo = ""

if user_input == "1":
    exo = "curl"
elif user_input == "2":
    exo = "squat"
elif user_input == "3":
    exo = "pushup"
"""
elif user_input == "5":
    exo = "pullup"
elif user_input == "6":
    exo = "situp"
"""

#exercices.start_projector(exo)
#exercices.start_cam(exo, rep)

def start_projector(exo):
    exercices.start_projector(exo)

def start_cam(exo, rep):
    exercices.start_cam(exo, rep)

videoProj = threading.Thread(target=start_projector, args=(exo,))
cam = threading.Thread(target=start_cam, args=(exo, rep))

videoProj.start()
cam.start()

print("Les deux fonctions ont été exécutées.")