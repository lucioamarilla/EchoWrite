import pyautogui
import pyperclip
import time

class TextTyper:

    def __init__(self, delay_inicial=3, auto_enter=True):
        self.delay_inicial = delay_inicial
        self.auto_enter = auto_enter

    def escribir(self, texto):
        if not texto:
            print("No hay texto para escribir")
            return

        print(f"Tienes {self.delay_inicial} segundos para seleccionar el campo...")
        time.sleep(self.delay_inicial)

        # Copiar al portapapeles
        pyperclip.copy(texto)

        # Pegar (Linux/Windows)
        pyautogui.hotkey('ctrl', 'v')

        if self.auto_enter:
            pyautogui.press('enter')

        print("Texto escrito correctamente")