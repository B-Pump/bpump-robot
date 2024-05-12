from time import time as timer, sleep
from io import BytesIO
from math import sqrt

from cv2 import VideoCapture, resize, imshow as cv2_show, waitKey, destroyAllWindows
from matplotlib.pyplot import figure, imshow as plt_show, scatter, axis, savefig
from PIL import Image
from ascii_magic import AsciiArt
from socketio import Server

from module.poseModule import poseModule
from module.imgModule import imgModule
from module.voiceModule import voiceModule

detector = poseModule()
imager = imgModule()
tts = voiceModule()

class Exercice:
    def __init__(self, video_dir = "./assets/workout", video_width = 640, video_height = 360, reps = -1, drop = False, image = "./assets/bg-white.jpg"):
        self.video_dir = video_dir
        self.video_width = video_width
        self.video_height = video_height

        self.reps = reps
        self.drop = drop

        self.image = Image.open(image)
        self.width, self.height = self.image.size
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        self.marker_size = 3500

    def start_cam(self, sio: Server, exercise_data, metabolism, is_rpi: bool):
        if is_rpi:
            from picamera2 import Picamera2 # type: ignore

            piCam = Picamera2()
            piCam.preview_configuration.main.size=(self.video_width, self.video_height)
            piCam.preview_configuration.main.format="RGB888"
            piCam.preview_configuration.align()
            piCam.configure("preview")
            piCam.start()
        else:
            cap = VideoCapture(f"{self.video_dir}/dips.mp4") # VideoCapture(0)
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

        user_height = None
        user_weight = None

        reps = exercise_data["reps"]
        rest = exercise_data["rest"]

        while self.reps < reps:
            if is_rpi:
                video = piCam.capture_array()
                success = True
            else:
                success, video = cap.read()

            if success:
                video = detector.findPose(video, False)
                video = resize(video, (self.video_width, self.video_height))

                lmList = detector.findPosition(video, False)

                if metabolism != None:
                    user_height = metabolism["height"]
                    user_weight = metabolism["weight"]

                    # Physics part
                    pS = detector.getPixelSize(video)
                    center_gravite = detector.findGravityPoint(video)
                    gCenterPosHistory.append((center_gravite[0], center_gravite[1], timer()))

                    if len(gCenterPosHistory) > 4:
                        # Acceleration
                        scale = (user_height / (100 * pS))
                        dS1 = tuple(map(lambda i, j: i - j, gCenterPosHistory[-3], gCenterPosHistory[-2]))
                        dvS1 = sqrt(dS1[0]**2 + dS1[1]**2)/(dS1[2]) * scale
                        dS2 = tuple(map(lambda i, j: i - j, gCenterPosHistory[-2], gCenterPosHistory[-1]))
                        dvS2 = sqrt(dS2[0]**2 + dS2[1]**2)/(dS2[2]) * scale
                        acc = (dvS2 - dvS1) / (dS1[2])

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
                        "leftArm": (11, 13, 15),
                        "rightArm": (12, 14, 16),

                        "leftForearm": (13, 15, 17),
                        "rightForearm": (14, 16, 18),

                        "leftHand": (15, 17, 19),
                        "rightHand": (16, 18, 20),

                        "leftLeg": (23, 25, 27),
                        "rightLeg": (24, 26, 28),

                        "leftFoot": (25, 27, 29),
                        "rightFoot": (26, 28, 30),

                        "leftBody": (11, 23, 25),
                        "rightBody": (12, 24, 26),
                    }

                    for angle_data in exercise_data["camera"]:
                        angle_name = angle_data["angle"]
                        min_angle = angle_data["min"]
                        max_angle = angle_data["max"]

                        if angle_name and angle_name in joint_indices:
                            new_angles = detector.findAngle(video, *joint_indices[angle_name], True)

                            normalized_angle = (new_angles - min_angle) / (max_angle - min_angle)
                            movement_percentage = int(normalized_angle * 100)

                            # print(f"Rep % ({angle_name}) : {movement_percentage}%") # debug purposes

                    if movement_percentage >= 95:
                        self.drop = False
                    elif movement_percentage <= 5 and not self.drop:
                        self.reps += 1
                        # print("Reps :", self.reps) # debug purposes
                        if self.reps > 0:
                            tts.playText(str(self.reps), is_rpi)

                        self.drop = True

                # out.write(video)
                cv2_show("bpump-cam", video)
                waitKey(1)
            else:
                break

        destroyAllWindows()

        if not is_rpi:
            cap.release()

        if metabolism != None :
            dataPacket = {
                "total_energy": totalEnergy,
                "energy": energyData, # J
                "speed": speedData, # m.s-1
                "force": forceData, # N
            }
            if sio:
                sio.emit("result", dataPacket)

        if rest != 0:
            tts.playText("Temps de repos", is_rpi)

            for i in range(rest, 0, -1):
                imager.clear_console()

                print(imager.asciier(str(i)))
                tts.playText(str(i), is_rpi)
                sleep(1)

            imager.clear_console()

            print(imager.asciier("C'est  reparti  !"))
            tts.playText("C'est reparti !", is_rpi)

        sleep(2)
        imager.clear_console()

    def start_proj(self, exercise_data: str):
        points = exercise_data["projector"]
        positions = [(point["x"], point["y"]) for point in points]

        adjusted_markers = {
            "workout": [(self.center_x + x, self.center_y + y) for x, y in positions]
        }

        figure(figsize=(self.width / 77, self.height / 77))
        plt_show(self.image)

        scatter(self.center_x, self.center_y, color="blue", marker="o", s=self.marker_size / 2)
        for point in adjusted_markers["workout"]:
            scatter(point[0], point[1], color="red", marker="o", s=self.marker_size)

        axis("off")

        image_buffer = BytesIO()
        savefig(image_buffer, bbox_inches="tight", pad_inches=0)
        image_buffer.seek(0)

        deformed_image = imager.deform(Image.open(image_buffer))

        AsciiArt.from_pillow_image(Image.fromarray(deformed_image)).to_terminal(columns=190, width_ratio=2)

        image_buffer.close()

if __name__ == "__main__":
    exercise_data = {
        'camera': [
            {
                "angle": "leftArm",
                "min": 160,
                "max": 80
            },
            {
                "angle": "rightArm",
                "min": 160,
                "max": 80
            }
        ],
        'projector': [
            {"x": 400, "y": 150},
            {"x": 400, "y": -150},
            {"x": -400, "y": 75},
            {"x": -400, "y": -75}
        ],
        'reps': 10,
        'rest': 2
    }

    Exercice().start_proj(exercise_data)
    Exercice().start_cam(None, exercise_data, {"weight": 70, "height": 172, "age": 18, "sex": "m"}, False)