import numpy as np
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write

sd.default.device = 8

class Record():
    
    def __init__(self, duracion, fs=48000):
        # Configuración
        self.duracion = duracion  # segundos
        self.fs = fs  # Frecuencia de muestreo (Hz)

    def grabar_audio(self):
        print(">>> GRABANDO ...")

        audio = sd.rec(int(self.duracion * self.fs),
                       samplerate=self.fs,
                       channels=1,
                       dtype='int16')
        
        sd.wait()
        print(">>> FIN")

        self.audio = audio  # guardamos en la instancia
        return audio

    def verificar_audio(self):
        if not hasattr(self, 'audio'):
            raise ValueError("Primero debes grabar el audio")

        max_val = np.max(self.audio)
        print("Nivel máximo:", max_val)

        if max_val < 50:
            print("Audio en silencio")
            return False
        
        return True

    def guardar_audio(self, filename=None):
        if not hasattr(self, 'audio'):
            raise ValueError("No hay audio para guardar")

        if filename is None:
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            filename = temp.name

        write(filename, self.fs, self.audio)
        print("Guardado en:", filename)

        return filename

    def grabar_proceso_completo(self):
        self.grabar_audio()

        if not self.verificar_audio():
            print("Grabación inválida")
            return None

        return self.guardar_audio()


