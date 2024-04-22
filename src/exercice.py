from time import time as timer, sleep
from io import BytesIO
from math import sqrt

from cv2 import VideoCapture, resize, imshow as cv2_show, waitKey, destroyAllWindows, getPerspectiveTransform, warpPerspective
from matplotlib.pyplot import figure, imshow as plt_show, scatter, axis, savefig
from numpy import float32, array
from PIL import Image
from ascii_magic import AsciiArt
from socketio import Server

from poseModule import poseModule
detector = poseModule()

class Exercice:
    def __init__(self, reps = -1, drop = False, image = "./assets/bg-white.jpg"):
        self.reps = reps
        self.drop = drop

        self.up_advice = False
        self.down_advice = False

        self.image = Image.open(image)
        self.width, self.height = self.image.size
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        self.marker_size = 3500

    def start_cam(self, sio: Server, exercise_data, reps: int, metabolism, is_rpi):
        if is_rpi:
            from picamera2 import Picamera2 # type: ignore

            piCam = Picamera2()
            piCam.preview_configuration.main.size=(640, 360)
            piCam.preview_configuration.main.format="RGB888"
            piCam.preview_configuration.align()
            piCam.configure("preview")
            piCam.start()
        else:
            cap = VideoCapture("./assets/workout.mp4")
            if not cap.isOpened():
                return

        print("Préparez-vous : L'exercice va bientôt démarrer")
        for i in range(1, 0, -1):
            print(f"Plus que {i} secondes...")
            sleep(1)

        gCenterPosHistory = []
        totalEnergy = 0
        speedData = []
        energyData = []
        forceData = []

        referenceTime = timer()
        last_chrono_rounded = None

        user_height = metabolism["height"]
        user_weight = metabolism["weight"]

        while self.reps < reps:
            if is_rpi:
                video = piCam.capture_array()
                if not video:
                    return
                success = True
            else:
                success, video = cap.read()

            if success:
                video = detector.findPose(video, False)
                video = resize(video, (512, 288))

                lmList = detector.findPosition(video, False)

                if user_height != None and user_weight != None:
                    # Physics part
                    pS = detector.getPixelSize(video)
                    center_gravite = detector.findGravityPoint(video, True)
                    gCenterPosHistory.append((center_gravite[0], center_gravite[1], timer()))

                    if len(gCenterPosHistory) > 4:
                        # Acceleration
                        scale = (user_height / (100*pS))
                        dS1 = tuple(map(lambda i, j: i - j, gCenterPosHistory[-3], gCenterPosHistory[-2]))
                        dvS1 = sqrt(dS1[0]**2 + dS1[1]**2)/(dS1[2]) * scale
                        dS2 = tuple(map(lambda i, j: i - j, gCenterPosHistory[-2], gCenterPosHistory[-1]))
                        dvS2 = sqrt(dS2[0]**2 + dS2[1]**2)/(dS2[2]) * scale
                        acc= (dvS2-dvS1) / (dS1[2])

                        # Work
                        dgcenter = tuple(map(lambda i, j: i - j, gCenterPosHistory[-1], gCenterPosHistory[-2]))
                        dDist = sqrt(dgcenter[0]**2 + dgcenter[1]**2)
                        dDistM = scale * (dDist)

                        # Force
                        Force = (user_weight * abs(acc) + 9.81)
                        Speed = dDist / dgcenter[2]
                        Energy = abs(dDistM) * Force * abs(dgcenter[2]) * (24 / 100)
                        totalEnergy += Energy # energy sum

                        # Data returns handling
                        chrono = timer() - referenceTime
                        chrono_rounded = round(chrono)

                        if chrono_rounded != last_chrono_rounded:
                            label = f"{chrono_rounded}s"
                            last_chrono_rounded = chrono_rounded
                        else:
                            label = ""

                        energyData.append({
                            "value": Energy, # J
                            "label": label
                        })
                        speedData.append({
                            "value": Speed, # m.s-1
                            "label": label
                        })
                        forceData.append({
                            "value": Force, # N
                            "label": label
                        })

                        # Speed in pixels per second
                        gCenterPosHistory.pop(0)

                if len(lmList) != 0:
                    joint_indices = {
                        "leftArm": (12, 14, 16),
                        "leftHip": (12, 24, 26),
                        "leftLeg": (24, 26, 28),
                        "leftFoot": (26, 28, 32),
                        "rightArm": (11, 13, 15),
                        "rightHip": (11, 23, 25),
                        "rightLeg": (23, 25, 27),
                        "rightFoot": (25, 27, 31)
                    }

                    for angle_data in exercise_data["camera"]:
                        angle_name = angle_data["angle"]
                        min_angle = angle_data["min"]
                        max_angle = angle_data["max"]

                        if angle_name and angle_name in joint_indices:
                            new_angles = detector.findAngle(video, *joint_indices[angle_name], True)

                            normalized_angle = (new_angles - min_angle) / (max_angle - min_angle)
                            movement_percentage = int(normalized_angle * 100)

                            # if movement_percentage >= 110 and not self.up_advice:
                            #     print("Tu es allé trop haut !")
                            #     self.up_advice = True
                            # elif movement_percentage <= -10 and not self.down_advice:
                            #     print("Tu es allé trop bas !")
                            #     self.down_advice = True

                            # print(f"Rep % ({angle_name}) : {movement_percentage}%")

                    if movement_percentage >= 95:
                        self.drop = False
                    elif movement_percentage <= 5 and not self.drop:
                        self.reps += 1
                        print("Reps :", self.reps)

                        self.drop = True
                        self.up_advice = False
                        self.down_advice = False

                cv2_show("bpump-cam", video)
                waitKey(1)

        destroyAllWindows()
        cap.release()

        if user_height != None and user_weight != None:
            dataPacket = {
                "total_energy": totalEnergy,
                "energy": energyData, # J
                "speed": speedData, # m.s-1
                "force": forceData, # N
            }
            sio.emit("result", dataPacket)

    def start_proj(self, sio: Server, exercise_data: str):
        workout = exercise_data["id"]

        positions = [(point["x"], point["y"]) for point in exercise_data["projector"]]
        markers = {workout: positions}

        adjusted_markers = {
            workout: [(self.center_x + x, self.center_y + y) for x, y in positions]
            for workout, positions in markers.items()
        }

        figure(figsize=(self.width / 77, self.height / 77))
        plt_show(self.image)

        scatter(self.center_x, self.center_y, color="blue", marker="o", s=self.marker_size / 2)
        for point in adjusted_markers[workout]:
            scatter(point[0], point[1], color="red", marker="o", s=self.marker_size)

        axis("off")

        image_buffer = BytesIO()
        savefig(image_buffer, bbox_inches="tight", pad_inches=0)
        image_buffer.seek(0)

        image = Image.open(image_buffer)
        minus_plus = 300

        width, height = image.size
        original_points = float32([[0, 0], [width, 0], [0, height], [width, height]])
        points_dest = float32([[0 + minus_plus, 0], [width - minus_plus, 0], [0, height], [width, height]])

        transformation_matrix = getPerspectiveTransform(original_points, points_dest)
        deformed_image = warpPerspective(array(image), transformation_matrix, (width, height))

        AsciiArt.from_pillow_image(Image.fromarray(deformed_image)).to_terminal(columns=190, width_ratio=2)

        image_buffer.close()

if __name__ == "__main__":
    exercise_data = {
        'id': 'pullups', 
        'icon': 'https://i.imgur.com/3tcCNOo.jpeg', 
        'description': 'Les tractions sont un exercice efficace pour renforcer les muscles du dos, des épaules et des bras. Accrochez-vous à une  barre fixe, tendez vos bras et tirez votre corps vers le haut en utilisant la force de vos muscles du dos et de vos bras.',
        'difficulty': 4, 
        'muscles': ['Dos', 'épaules', 'Bras'], 
        'needed': ['Barre fixe'], 
        'camera': [
            {
                "angle": "leftArm",
                "min": 160,
                "max": 45
            },
            {
                "angle": "rightArm",
                "min": 160,
                "max": 45
            }
        ],
        'title': 'Tractions', 
        'exo_id': 4, 
        'category': 'Haut du corps', 
        'video': 'https://bpump-web.vercel.app/video/pullups.mp4', 
        'security': ['Maintenez une bonne forme avec  les épaules en arrière.', 'Évitez de balancer votre corps pour faciliter le mouvement.'],
        'projector': [
            {
                "x": 400,
                "y": 150
            },
            {
                "x": 400,
                "y": -150
            },
            {
                "x": -400,
                "y": 75
            },
            {
                "x": -400,
                "y": -75
            }
        ]
    }

    # Exercice().start_proj(exercise_data)
    Exercice().start_cam(None, exercise_data, 8, {"weight": 70, "height": 172, "age": 18, "sex": "m"}, False)