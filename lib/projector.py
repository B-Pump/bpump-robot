from PIL import Image
import matplotlib.pyplot as plt
import internals.expectations as data
import internals.deformation as deform


class Projetor:
    """
    
    """
    def __init__(self):
        image = Image.open("assets/fond-blanc.png")

        width, height = image.size
        print(f"Width:{width}\nHeight:{height}")

        center_x = width / 2
        center_y = height / 2

        marker_size = 500
    
    def x(self):
        pass