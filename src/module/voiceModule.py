from threading import Thread

from simpleaudio import WaveObject

class voiceModule():
    def __init__(self):
        pass

    def playAudio(self, file: str):
        def play():
            wave_obj = WaveObject.from_wave_file(f"./assets/voices/{file}.wav")
            play_obj = wave_obj.play()
            play_obj.wait_done()
        
        audio_thread = Thread(target=play)
        audio_thread.start()