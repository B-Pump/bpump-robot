import threading
from pyttsx3 import init as ttsInit

class voiceModule() :
    def __init__(self):
        self.engine = ttsInit()
        self.voices = self.engine.getProperty("voices")

    def playText(self, text: str, is_rpi: bool):
        def play_in_thread():
            self.engine.setProperty("rate", 250)

            if is_rpi:
                self.engine.setProperty("voice", self.voices[29].id)
            else:
                self.engine.setProperty("voice", self.voices[0].id)

            if not self.engine._inLoop:
                self.engine.say(str(text))
                self.engine.runAndWait()
                self.engine.stop()

        thread = threading.Thread(target=play_in_thread)
        thread.start()