from faster_whisper import WhisperModel

class Transcriber:

    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

    def transcribir(self, ruta_audio):
        print(">>> PROCESANDO CON WHISPER...")

        segments, info = self.model.transcribe(
            ruta_audio,
            language="es",
            task="transcribe",
            vad_filter=True,
            beam_size=5
        )

        texto = ""
        for segment in segments:
            texto += segment.text + " "

        resultado = texto.strip()
        print(f"\n>>> RESULTADO: {resultado}")

        return resultado
    