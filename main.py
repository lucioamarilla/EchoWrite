from Record import Record
from Transcriber import Transcriber
from SpeechRecognizer import SpeechRecognizer
from TextTyper import TextTyper
from dotenv import load_dotenv
import os

load_dotenv()

hf_token = os.getenv("HF_TOKEN")

recorder = Record(duracion=6, fs=48000)
transcriber = Transcriber(model_size="medium")
recognizer = SpeechRecognizer(recorder, transcriber)

typer = TextTyper(delay_inicial=5)

while True:
    texto = recognizer.reconocer()

    if texto:
        typer.escribir(texto)

    continuar = input("\n¿Continuar? (s/n): ").lower()
    if continuar != 's':
        break