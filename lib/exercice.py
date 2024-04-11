import sys, time, io

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from ascii_magic import AsciiArt

sys.path.append('../bpump-robot')

import lib.internals.poseModule as pm

detector = pm.poseModule()

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

    def start_cam(self, exercise_data, reps: int):
        cap = cv2.VideoCapture("./assets/workout.mp4")
        if not cap.isOpened():
            return

        print("Préparez-vous : L'exercice va bientôt démarrer")
        for i in range(2, 0, -1):
            print(f"Plus que {i} secondes...")
            time.sleep(1)

        while self.reps < reps:
            success, video = cap.read()

            if success:
                video = detector.findPose(video, False)
                # video = cv2.resize(video, (1024, 576))

                lmList = detector.findPosition(video, False)

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

                # cv2.imshow("bpump-cam", video)
                # cv2.waitKey(1)
            else:
                cap.release()
                # cv2.destroyAllWindows()
                # sys.exit(1)

    def start_proj(self, exercise_data: str):
        workout = exercise_data["id"]

        positions = [(point["x"], point["y"]) for point in exercise_data["projector"]]
        markers = {workout: positions}

        adjusted_markers = {
            workout: [(self.center_x + x, self.center_y + y) for x, y in positions]
            for workout, positions in markers.items()
        }

        plt.figure(figsize=(self.width / 77, self.height / 77))
        plt.imshow(self.image)

        plt.scatter(self.center_x, self.center_y, color="blue", marker="o", s=self.marker_size / 2)
        for point in adjusted_markers[workout]:
            plt.scatter(point[0], point[1], color="red", marker="o", s=self.marker_size)

        plt.axis("off")

        image_buffer = io.BytesIO()
        plt.savefig(image_buffer, bbox_inches="tight", pad_inches=0)
        image_buffer.seek(0)

        image = Image.open(image_buffer)
        minus_plus = 300

        width, height = image.size
        original_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        points_dest = np.float32([[0 + minus_plus, 0], [width - minus_plus, 0], [0, height], [width, height]])

        transformation_matrix = cv2.getPerspectiveTransform(original_points, points_dest)
        deformed_image = cv2.warpPerspective(np.array(image), transformation_matrix, (width, height))

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
        'calories': 15,
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

    Exercice().start_proj(exercise_data)
    Exercice().start_cam(exercise_data, 4)