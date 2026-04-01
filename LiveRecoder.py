import sounddevice as sd
import numpy as np
import tempfile
from scipy.io.wavfile import write
from Record import Record

class LiveRecorder(Record):

    def __init__(self, fs=48000):
        super().__init__(duracion=0, fs=fs)  # duracion ya no importa
        self.frames = []
        self.stream = None
        self.grabando = False

    def _callback(self, indata, frames, time, status):
        if self.grabando:
            self.frames.append(indata.copy())

    def iniciar_grabacion(self):
        self.frames = []
        self.grabando = True

        self.stream = sd.InputStream(
            samplerate=self.fs,
            channels=1,
            dtype='int16',
            callback=self._callback
        )

        self.stream.start()
        print(">>> GRABANDO (manual)...")

    def detener_grabacion(self):
        if not self.grabando:
            return None

        self.grabando = False
        self.stream.stop()
        self.stream.close()

        print(">>> FIN")

        if not self.frames:
            return None

        audio = np.concatenate(self.frames, axis=0)
        self.audio = audio

        return audio

    def grabar_proceso_manual(self):
        """
        Equivalente a grabar_proceso_completo pero controlado manualmente
        """
        if not hasattr(self, 'audio'):
            return None

        if not self.verificar_audio():
            print("Grabación inválida")
            return None

        return self.guardar_audio()