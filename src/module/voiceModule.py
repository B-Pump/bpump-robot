from pyttsx3 import init as ttsInit

class voiceModule():
    def __init__(self):
        self.engine = ttsInit()
        self.voices = self.engine.getProperty("voices")

    def playText(self, text: str, is_rpi: bool):
        self.engine.setProperty("rate", 250)

        if is_rpi:
            self.engine.setProperty("voice", self.voices[29].id)
        else:
            self.engine.setProperty("voice", self.voices[0].id)

        self.engine.say(str(text))
        self.engine.runAndWait()
        self.engine.stop()