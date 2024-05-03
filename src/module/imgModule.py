from os import system, name as os_name

from cv2 import getPerspectiveTransform, warpPerspective
from numpy import float32, array
from shutil import get_terminal_size
from art import text2art

class imgModule() :
    def __init__(self):
        pass
    
    def clear_console(self):
        system("cls" if os_name == "nt" else "clear")

    def deform(self, image, minus_plus=300):
        """
        Deforms an image by applying a perspective transformation.

        :param image: The image to deform.
        :param minus_plus: The deformation value (300 by default).
        :return: The deformed image.
        """

        width, height = image.size
        original_points = float32([[0, 0], [width, 0], [0, height], [width, height]])
        points_dest = float32([[0 + minus_plus, 0], [width - minus_plus, 0], [0, height], [width, height]])

        transformation_matrix = getPerspectiveTransform(original_points, points_dest)
        deformed_image = warpPerspective(array(image), transformation_matrix, (width, height))

        return deformed_image
    
    def asciier(self, text) -> str:
        """
        Converts text into ASCII art

        :param text: The text to convert to ASCII art.
        :return: The centered ASCII art representation of the text.
        """

        console_size = get_terminal_size()

        lines = text2art(text, font="roman").split("\n")
        space_top = (console_size.lines - len(lines)) // 2
        space_left = (console_size.columns - len(lines[0])) // 2

        return "\n" * space_top + "\n".join([" " * space_left + line for line in lines])