import qrcode

class QRCode:
    def __init__(self):
        pass

    def generate(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            border=3,
        )

        qr.add_data(data)
        qr.make(fit=True)

        qr_str = qr.get_matrix()
        print("\n".join(["".join(["██" if cell else "  " for cell in row]) for row in qr_str]))