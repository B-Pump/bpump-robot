import cv2  # Importing the OpenCV module
import numpy as np  # Importing the NumPy module
import keyboard  # Importing the keyboard module
import os  # Importing the os module

class Counter:
    def __init__(self):
        self.minus_plus = 0

# Deforming the image
def deformImage(workout):
    filePath = f"./data/{workout}.png"
    folderPath = "./output"

    image = cv2.imread(filePath)
    
    if image is not None:
        height, width = image.shape[:2]
        print(height, width)  # Printing height and width of the image (testing)
        original_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        counter = Counter()

        # Updating destination points
        def update_points_dest():
            nonlocal counter
            return np.float32([[0 + counter.minus_plus, 0], [width - counter.minus_plus, 0], [0, height], [width, height]])

        # Keyboard action
        def keyboard_action(event):
            nonlocal counter
            if event.name == "a":
                counter.minus_plus -= 10
            elif event.name == "z":
                counter.minus_plus += 10

        keyboard.on_press(keyboard_action)

        while True:
            points_dest = update_points_dest()
            transformation_matrix = cv2.getPerspectiveTransform(original_points, points_dest)
            deformed_image = cv2.warpPerspective(image, transformation_matrix, (width, height))
            cv2.namedWindow("Point Display", cv2.WINDOW_NORMAL)  # Creating a resizable window
            cv2.setWindowProperty("Point Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)  # Fullscreen mode
            cv2.imshow("Point Display", deformed_image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cv2.destroyAllWindows()

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        cv2.imwrite(f"{folderPath}/{workout}.png", deformed_image)
        os.remove(filePath)

        return f"Image deformed successfully in: {folderPath}/{workout}.png"

    return "Error: Unable to load the initial image"