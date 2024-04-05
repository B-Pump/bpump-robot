import os, sys

import qrcode, cv2

sys.path.append('../bpump-robot')

import lib.ansi as ansi

class QRCode:
    def __init__(self):
        pass

    def generate(self, data, filename="qr_code"):
        folderPath = "./output"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )

        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        img.save(f"{folderPath}/{filename}.jpg")
        ansi.image_to_ansi(f"{folderPath}/{filename}.jpg")

    def read(self, image_path):
        img = cv2.imread(image_path)
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)

        if bbox is not None:
            return data