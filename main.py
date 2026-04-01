# main.py MODIFICADO con diseño estilo Chat Input 3
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QFrame, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QColor

# Importación de tus módulos existentes
from LiveRecoder import LiveRecorder
from Transcriber import Transcriber
from TextTyper import TextTyper
from SpeechRecognizer import SpeechRecognizer

from dotenv import load_dotenv
import os

load_dotenv()

hf_token = os.getenv("HF_TOKEN")
class TranscriptionWorker(QThread):
    """Hilo para procesar la voz sin congelar la interfaz"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, recognizer, audio_path):
        super().__init__()
        self.recognizer = recognizer
        self.audio_path = audio_path

    def run(self):
        try:
            texto = self.recognizer.transcriber.transcribir(self.audio_path)
            if os.path.exists(self.audio_path):
                os.remove(self.audio_path)
            self.finished.emit(texto)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dictado por Voz")
        self.setMinimumSize(600, 500)
        
        # Inicialización de componentes
        self.recorder = LiveRecorder()
        self.transcriber = Transcriber(model_size="medium")
        self.typer = TextTyper(delay_inicial=0)
        self.recognizer = SpeechRecognizer(self.recorder, self.transcriber)

        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- BARRA DE ENTRADA ESTILO CHAT (Superior) ---
        self.input_bar = QFrame()
        self.input_bar.setObjectName("inputBar")
        self.input_bar.setMinimumHeight(60)
        input_layout = QHBoxLayout(self.input_bar)
        input_layout.setContentsMargins(15, 0, 15, 0)

        # Placeholder / Estado de grabación (Imagen 0: "Ask anything")
        self.mic_status_label = QLabel("Presiona el micro para hablar...")
        self.mic_status_label.setObjectName("micStatusLabel")
        input_layout.addWidget(self.mic_status_label)
        
        input_layout.addStretch() # Empuja los botones a la derecha

        # Botón Micrófono Principal (Imagen 0)
        self.mic_btn = QPushButton()
        self.mic_btn.setObjectName("micButton")
        self.mic_btn.setFixedSize(40, 40)
        self.mic_btn.setCursor(Qt.PointingHandCursor)
        # Usamos texto plano si no tienes iconos, pero está estilizado como círculo
        self.mic_btn.setText("🎤") 
        self.mic_btn.clicked.connect(self._start_recording_flow)
        input_layout.addWidget(self.mic_btn)

        # Controles de Grabación Activa (Imagen 1: X y Palomita)
        # Se crean ocultos por defecto
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setFixedSize(40, 40)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self._cancel_recording)
        self.cancel_btn.hide()
        input_layout.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton("✓")
        self.confirm_btn.setObjectName("confirmButton")
        self.confirm_btn.setFixedSize(40, 40)
        self.confirm_btn.setCursor(Qt.PointingHandCursor)
        self.confirm_btn.clicked.connect(self._confirm_and_process)
        self.confirm_btn.hide()
        input_layout.addWidget(self.confirm_btn)

        # Efecto de sombra para la barra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.input_bar.setGraphicsEffect(shadow)

        main_layout.addWidget(self.input_bar)


        # --- ÁREA DE RESULTADOS (Central) ---
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("La transcripción aparecerá aquí...")
        main_layout.addWidget(self.text_edit)

        # Botón para escribir
        self.write_btn = QPushButton("⌨️ ESCRIBIR EN OTRA VENTANA")
        self.write_btn.setObjectName("writeButton")
        self.write_btn.setMinimumHeight(50)
        self.write_btn.setCursor(Qt.PointingHandCursor)
        self.write_btn.clicked.connect(self._start_typing_countdown)
        main_layout.addWidget(self.write_btn)

        self.setStyleSheet(self._get_stylesheet())

    # --- LÓGICA DE FLUJO ---

    def _start_recording_flow(self):
        """Imagen 0 -> Transición a Grabando"""
        # UI: Cambiar placeholder y ocultar micro, mostrar X y ✓
        self.mic_status_label.setText("🛑 Grabando audio... (Confirma o Cancela)")
        self.mic_status_label.setStyleSheet("color: #ff4b2b; font-weight: bold;")
        self.mic_btn.hide()
        self.cancel_btn.show()
        self.confirm_btn.show()

        # Lógica: Iniciar grabación
        self.recorder.iniciar_grabacion()

    def _cancel_recording(self):
        """Botón X -> Cancelar y volver al estado inicial"""
        # Lógica: Detener sin guardar
        self.recorder.detener_grabacion()
        self.recorder.frames = [] # Limpiar buffer
        
        # UI: Volver a Imagen 0
        self._reset_input_bar()

    def _confirm_and_process(self):
        """Botón ✓ -> Detener y transcribir"""
        # UI: Bloquear controles y avisar procesamiento
        self.cancel_btn.setEnabled(False)
        self.confirm_btn.setEnabled(False)
        self.mic_status_label.setText("⏳ Procesando con Whisper...")
        self.mic_status_label.setStyleSheet("color: #f39c12;")

        # Lógica: Obtener audio
        self.recorder.detener_grabacion()
        ruta_audio = self.recorder.guardar_audio() 
        
        if ruta_audio:
            self._start_worker(ruta_audio)
        else:
            self._on_complete("No se detectó audio válido.")

    def _reset_input_bar(self):
        """Vuelve la barra superior al estado 'Ask anything'"""
        self.mic_status_label.setText("Presiona el micro para hablar...")
        self.mic_status_label.setStyleSheet("color: #888;")
        self.mic_btn.show()
        self.cancel_btn.hide()
        self.cancel_btn.setEnabled(True)
        self.confirm_btn.hide()
        self.confirm_btn.setEnabled(True)

    # --- LÓGICA DE PROCESAMIENTO ---

    def _start_worker(self, ruta_audio):
        self.worker = TranscriptionWorker(self.recognizer, ruta_audio)
        self.worker.finished.connect(self._on_complete)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_complete(self, text):
        self.text_edit.setText(text)
        self._reset_input_bar() # Restaurar barra superior
        QMessageBox.information(self, "Listo", "Transcripción completa.")

    def _on_error(self, error):
        QMessageBox.critical(self, "Error", f"Fallo: {error}")
        self._reset_input_bar()

    def _start_typing_countdown(self):
            texto = self.text_edit.toPlainText().strip()
            if not texto: 
                return

            # Bloqueamos el botón para evitar múltiples clics
            self.write_btn.setEnabled(False)
            
            # Configuramos el tiempo inicial (3 segundos)
            self.countdown_v = 5
            
            # Creamos un timer que se ejecute cada segundo
            self.typing_timer = QTimer(self)
            self.typing_timer.timeout.connect(lambda: self._update_countdown(texto))
            
            # Mostramos el primer mensaje inmediatamente
            self.write_btn.setText(f"Cambiando ventana en {self.countdown_v}s...")
            self.typing_timer.start(1000) # Se dispara cada 1000ms

    def _update_countdown(self, texto):
        self.countdown_v -= 1
        
        if self.countdown_v > 0:
            # Actualizamos el texto del botón con el tiempo restante
            self.write_btn.setText(f"Cambie de ventana en {self.countdown_v}s...")
        else:
            # Cuando llega a 0, detenemos el timer y ejecutamos la escritura
            self.typing_timer.stop()
            self._execute_write(texto)

    def _execute_write(self, texto):
        self.typer.escribir(texto)
        self.write_btn.setText("⌨️ ESCRIBIR EN OTRA VENTANA")
        self.write_btn.setEnabled(True)

    def _get_stylesheet(self):
        return """
            QMainWindow { background-color: #121212; }
            QWidget { color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
            
            /* Estilo de la barra superior estilo Chat Input */
            QFrame#inputBar {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 30px; /* Bordes muy redondeados pill-shape */
            }
            QLabel#micStatusLabel {
                color: #888;
                font-size: 15px;
                background: transparent;
            }

            /* Botones circulares dentro de la barra */
            QPushButton#micButton, QPushButton#cancelButton, QPushButton#confirmButton {
                border: none;
                border-radius: 20px; /* Círculo perfecto */
                font-size: 18px;
            }
            
            /* Botón Micrófono (Imagen 0) */
            QPushButton#micButton {
                background-color: #f0f0f0;
                color: #121212;
            }
            QPushButton#micButton:hover { background-color: #ffffff; }

            /* Botón Cancelar X (Imagen 1) */
            QPushButton#cancelButton {
                background-color: transparent;
                color: #ff4b2b;
                font-weight: bold;
            }
            QPushButton#cancelButton:hover { background-color: rgba(255, 75, 43, 0.1); }

            /* Botón Confirmar ✓ (Imagen 1) */
            QPushButton#confirmButton {
                background-color: #00adb5;
                color: #121212;
                font-weight: bold;
            }
            QPushButton#confirmButton:hover { background-color: #00cfd8; }

            /* Resto de la UI */
            QTextEdit { 
                background-color: #1e1e1e; 
                border: 1px solid #333;
                border-radius: 10px; 
                padding: 10px; 
                color: #fff;
            }
            QPushButton#writeButton {
                background-color: #333;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton#writeButton:hover { background-color: #444; }
            QPushButton#writeButton:disabled { background-color: #222; color: #555; }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Ajuste de fuente global para iconos unicode
    font = QFont("Segoe UI Symbol", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())