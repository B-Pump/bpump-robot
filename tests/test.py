import threading, sys

sys.path.append('../bpump-robot')

from lib.exercice import Exercice

exercice = Exercice()

todo = ""

user_input = input("Quel exercice veux-tu faire et combien de répétitions ?\n1 - Tractions\n2 - Curls\n3 - Pompes\n4 - Sit-up\n5 - Squats\n\nFormat : <exo> <reps>\n\nRéponse : ")
user_input = user_input.split()

if len(user_input) == 2:
    exo, reps = user_input
    reps = int(reps)

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

    def start_cam(todo, rep):
        exercice.start_cam(todo, rep)

    #videoProj = threading.Thread(target=start_projector, args=(todo,))
    cam = threading.Thread(target=start_cam, args=(todo, reps))

    cam.start()
    start_projector(todo)
    
    print("Les deux threads ont bien été lancés !")
else:
    print("Vous avez mal répondu au formulaire")