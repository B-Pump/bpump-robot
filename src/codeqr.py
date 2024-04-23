import qrcode
from cv2 import QRCodeDetector, imread

class QRCode:
    def __init__(self):
        pass

    def generate(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            border=1,
        )

        qr.add_data(data)
        qr.make(fit=True)

        qr_str = qr.get_matrix()
        print("\n".join(["".join(["  " if cell else "██" for cell in row]) for row in qr_str]))

    def read(self, image_path: str):
        img = imread(image_path)
        detector = QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)

        if bbox is not None:
            return data