import os
import sys
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

sys.path.append('../bpump-robot')

import lib.internals.expectations as data
import lib.internals.poseHandler as ph
import lib.internals.poseModule as pm
import lib.ansi as ansi

class Exercice:
    def __init__(self, reps=0):
        self.reps = reps

        self.image = Image.open("./assets/bg-white.jpg")
        self.width, self.height = self.image.size
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        self.marker_size = 3500

    def start_cam(self, workout: str, reps: int):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return

        invert = data.fetchInvert(workout)
        neededAngles = data.fetchAngles(workout)

        detector = pm.poseModule()
        handler = ph.poseHandler()

        pTime = 0
        repDrop = False

        if invert:
            def calculate_progress(angle, angleMin, angleMax):
                angle = max(angleMin, min(angle, angleMax))
                progression = round(((angle - angleMax) / (angleMin - angleMax)) * 105)

                return progression
        else:
            def calculate_progress(angle, angle_min, angle_max):
                angle = max(angle_max, min(angle, angle_min))
                progression = round(((angle - angle_min) / (angle_max - angle_min)) * 100)

                return progression
            
        while self.reps < reps:
            success, img = cap.read()

            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime

            if success:
                img = detector.findPose(img, False)
                img = cv2.resize(img, (1024, 576))

                lmList = detector.findPosition(img, False)
                
                if len(lmList) != 0:
                    pose = handler.poseHandler(img, detector, neededAngles)
                    expectations = data.lookup(workout, pose)
                    percentage = calculate_progress(*expectations[0])

                    if percentage >= 100 and repDrop == True:
                        self.reps += 1
                        repDrop = False
                    elif percentage == 0:
                        repDrop = True

                    print(f"{round(fps)} ips | {percentage}% - Répétitions : {self.reps}")

                cv2.imshow("bpump-cam", img)
                cv2.waitKey(1)
            else:
                cap.release()
                cv2.destroyAllWindows()

        return reps

    def start_proj(self, workout: str):
        filePath = f"./data/{workout}.jpg"
        folderPath = "./output"

        if not os.path.exists(f"{folderPath}/{workout}.jpg"):
            positions = data.fetchPosition(workout)
            markers = {workout: positions}

            adjusted_markers = {
                workout: [(self.center_x + x, self.center_y + y) for x, y in positions]
                for workout, positions in markers.items()
            }

            plt.figure(figsize=(self.width / 77, self.height / 77))
            plt.imshow(self.image)

            plt.scatter(self.center_x, self.center_y, color="blue", marker="o", s=self.marker_size)

            for point in adjusted_markers[workout]:
                plt.scatter(point[0], point[1], color="red", marker="o", s=self.marker_size)

            plt.axis("off")

            plt.savefig(filePath, bbox_inches="tight", pad_inches=0)

            image = cv2.imread(filePath)
            minus_plus = 300

            height, width = image.shape[:2]
            original_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

            points_dest = np.float32([[0 + minus_plus, 0], [width - minus_plus, 0], [0, height], [width, height]])
            transformation_matrix = cv2.getPerspectiveTransform(original_points, points_dest)
            deformed_image = cv2.warpPerspective(image, transformation_matrix, (width, height))

            if not os.path.exists(folderPath):
                os.makedirs(folderPath)

            cv2.imwrite(f"{folderPath}/{workout}.jpg", deformed_image)
            os.remove(filePath)
        else:
            deformed_image = cv2.imread(f"{folderPath}/{workout}.jpg")
        
        ansi.image_to_ansi(f"./{folderPath}/{workout}.jpg")