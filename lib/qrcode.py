import qrcode
import os
from pyzbar.pyzbar import decode
from PIL import Image

class QRCode:
    """
    
    """
    def generate_qr_code(data):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=15, border=2)

        qr.add_data(data)
        qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save("./data/qr_code.png")
        print(data)

        print("QR Code generated successfully")
    
    
    def read_qr_code(path):
        if os.path.exists(path):
            for obj in decode(Image.open(path)):
                print("Decoded QR Code:", obj.data.decode("utf-8"))
                return obj.data.decode("utf-8")
        else:
            print("Image not found")