from cv2 import getPerspectiveTransform, warpPerspective
from numpy import float32, array

class imgModule() :
    def __init__(self):
        pass

    def deform(self, image, minus_plus=300):
        width, height = image.size
        original_points = float32([[0, 0], [width, 0], [0, height], [width, height]])
        points_dest = float32([[0 + minus_plus, 0], [width - minus_plus, 0], [0, height], [width, height]])

        transformation_matrix = getPerspectiveTransform(original_points, points_dest)
        deformed_image = warpPerspective(array(image), transformation_matrix, (width, height))

        return deformed_image