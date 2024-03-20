import qrcode
import os
from pyzbar.pyzbar import decode
from PIL import Image

class QRCode:
    def generate(data):
        folderPath = "./output"
        fileName = "qr_code.jpg"
        
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=15, border=2)

        qr.add_data(data)
        qr.make(fit=True)

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        qr.make_image(fill_color="black", back_color="white").save(f"{folderPath}/{fileName}")

        print(f"QR Code generated successfully in : {folderPath}/{fileName}")

    def read(path):
        if os.path.exists(path):
            for obj in decode(Image.open(path)):
                print("Decoded QR Code :", obj.data.decode("utf-8"))

                return obj.data.decode("utf-8")
        else:
            print("Error : Image not found")
            return