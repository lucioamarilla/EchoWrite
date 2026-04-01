import os

class SpeechRecognizer:

    def __init__(self, recorder, transcriber):
        self.recorder = recorder
        self.transcriber = transcriber

    def reconocer(self):
        try:
            archivo = self.recorder.grabar_proceso_completo()

            if archivo is None:
                return None

            texto = self.transcriber.transcribir(archivo)

            os.remove(archivo)

            return texto

        except Exception as e:
            print(f">>> ERROR: {e}")
            return None
        
