import sys, time

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

sys.path.append('../bpump-robot')

import lib.internals.poseModule as pm
import lib.ansi as ansi

detector = pm.poseModule()

class Exercice:
    def __init__(self, reps=0, image="./assets/bg-white.jpg", marker_size=3500):
        self.reps = reps

        self.image = Image.open(image)
        self.width, self.height = self.image.size
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        self.marker_size = marker_size

    def start_cam(self, exercise_data, reps: int):
        cap = cv2.VideoCapture("./assets/workout.mp4")
        if not cap.isOpened():
            return

        exo_camera = exercise_data["camera"]

        print("Préparez-vous : L'exercice va bientôt démarrer")
        for i in range(2, 0, -1):
            print(f"Plus que {i} secondes...")
            time.sleep(1)

        while self.reps < reps:
            success, video = cap.read()

            if success:
                video = detector.findPose(video, True)
                video = cv2.resize(video, (1024, 576))

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

                    for side in exo_camera:
                        angle_data = exo_camera.get(side, {})
                        if angle_data:
                            angle_name = angle_data["angle"]
                            min_angle = angle_data["minAngle"]
                            max_angle = angle_data["maxAngle"]

                            if angle_name and angle_name in joint_indices:
                                joint_index = joint_indices[angle_name]

                                angle = detector.findAngle(video, *joint_index)

                                # print(f"Angle of {angle_name} : {angle}")
                                # print(f"Minimal allowed angle : {min_angle}")
                                # print(f"Maximal allowed angle : {max_angle}")

                                #TODO: rep counter + percentage of rep for each angle

                cv2.imshow("bpump-cam", video)
                cv2.waitKey(1)
            else:
                cap.release()
                cv2.destroyAllWindows()
                sys.exit(1)

    # def start_proj(self, workout: str):
    #     filePath = f"./data/{workout}.jpg"
    #     folderPath = "./output"

    #     if not os.path.exists(f"{folderPath}/{workout}.jpg"):
    #         positions = data.fetchPosition(workout)
    #         markers = {workout: positions}

    #         adjusted_markers = {
    #             workout: [(self.center_x + x, self.center_y + y) for x, y in positions]
    #             for workout, positions in markers.items()
    #         }

    #         plt.figure(figsize=(self.width / 77, self.height / 77))
    #         plt.imshow(self.image)

    #         plt.scatter(self.center_x, self.center_y, color="blue", marker="o", s=self.marker_size)

    #         for point in adjusted_markers[workout]:
    #             plt.scatter(point[0], point[1], color="red", marker="o", s=self.marker_size)

    #         plt.axis("off")

    #         plt.savefig(filePath, bbox_inches="tight", pad_inches=0)

    #         image = cv2.imread(filePath)
    #         minus_plus = 300

    #         height, width = image.shape[:2]
    #         original_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

    #         points_dest = np.float32([[0 + minus_plus, 0], [width - minus_plus, 0], [0, height], [width, height]])
    #         transformation_matrix = cv2.getPerspectiveTransform(original_points, points_dest)
    #         deformed_image = cv2.warpPerspective(image, transformation_matrix, (width, height))

    #         if not os.path.exists(folderPath):
    #             os.makedirs(folderPath)

    #         cv2.imwrite(f"{folderPath}/{workout}.jpg", deformed_image)
    #         os.remove(filePath)
    #     else:
    #         deformed_image = cv2.imread(f"{folderPath}/{workout}.jpg")
        
    #     ansi.image_to_ansi(f"./{folderPath}/{workout}.jpg")

if __name__ == "__main__":
    exercise_data = {
        'id': 'pullups', 
        'icon': 'https://i.imgur.com/3tcCNOo.jpeg', 
        'description': 'Les tractions sont un exercice efficace pour renforcer les muscles du dos, des épaules et des bras. Accrochez-vous à une  barre fixe, tendez vos bras et tirez votre corps vers le haut en utilisant la force de vos muscles du dos et de vos bras.',
        'difficulty': 4, 
        'muscles': ['Dos', 'épaules', 'Bras'], 
        'needed': ['Barre fixe'], 
        'camera': {
            'left': {'angle': 'leftArm', 'minAngle': 150, 'maxAngle': 48}, 
            'right': {'angle': 'rightArm', 'minAngle': 150, 'maxAngle': 48}
        }, 
        'title': 'Tractions', 
        'exo_id': 4, 
        'category': 'Haut du corps', 
        'video': 'https://bpump-web.vercel.app/video/pullups.mp4', 
        'security': ['Maintenez une bonne forme avec  les épaules en arrière.', 'Évitez de balancer votre corps pour faciliter le mouvement.'],
        'calories': 15,
        'projector': [{'x': 100, 'y': 0}, {'x': -100, 'y': 0}]
    }

    Exercice().start_cam(exercise_data, 10)