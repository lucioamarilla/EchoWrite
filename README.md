# 🎙️ EchoWrite: Voice-to-Action Desktop Assistant

[cite_start]**EchoWrite** es una herramienta de productividad avanzada que permite dictar textos mediante inteligencia artificial y "escribirlos" automáticamente en cualquier aplicación activa[cite: 1]. [cite_start]Utiliza modelos de **Faster-Whisper** para garantizar una transcripción precisa y eficiente, ideal para desarrolladores, escritores o cualquier usuario que busque agilizar su flujo de trabajo[cite: 1].

[cite_start]La interfaz está construida con **PyQt5**, ofreciendo una experiencia moderna inspirada en barras de chat inteligentes con estados visuales claros[cite: 1].

---

## ✨ Características Principales

* [cite_start]**IA de Transcripción Dual**: Soporta modelos `base` (máxima velocidad y ligereza) y `medium` (alta precisión para dictados complejos)[cite: 1].
* [cite_start]**Escritura Automática**: Simula pulsaciones de teclado para volcar el texto en otras ventanas tras un conteo regresivo[cite: 1].
* [cite_start]**Procesamiento Asíncrono**: Ejecuta la IA en un hilo separado (`QThread`) para mantener la fluidez de la interfaz[cite: 1].
* [cite_start]**VAD (Voice Activity Detection)**: Filtra silencios y ruidos para una limpieza óptima del audio[cite: 1].

---

## 🛠️ Requisitos e Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd echowrite
```

### 2. Configuración de Entorno
Crea un archivo `.env` en la raíz del proyecto para facilitar la descarga del modelo `medium` mediante la API de Hugging Face:
```env
HF_TOKEN=tu_token_aquí
```

### 3. Instalación por Sistema Operativo

#### **Windows** 🪟
1.  Instala [FFmpeg](https://ffmpeg.org/download.html) y asegúrate de añadirlo al `PATH` del sistema.
2.  Instala las dependencias de Python:
    ```bash
    pip install -r requirements.txt
    ```

#### **Linux (Debian/Ubuntu)** 🐧
1.  Instala las librerías de desarrollo de audio:
    ```bash
    sudo apt install portaudio19-dev python3-pyaudio
    ```
2.  Instala las dependencias de Python:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Configuración de la IA (Whisper)

En `main.py`, puedes configurar la potencia del motor según tus necesidades:

* **Modelo `base`**: Ideal para hardware modesto. [cite_start]Es rápido pero puede omitir matices técnicos[cite: 1].
* **Modelo `medium`**: Recomendado para máxima precisión. [cite_start]La API Key de Hugging Face facilita su descarga y gestión[cite: 1].

### Aceleración por Hardware (NVIDIA GPU) ⚡
Si posees una tarjeta NVIDIA con núcleos CUDA, puedes optimizar el rendimiento editando `Transcriber.py`:

```python
self.model = WhisperModel(
    model_size,
    device="cuda",      # Cambiar "cpu" por "cuda"
    compute_type="float16" # Recomendado para GPUs modernas
)
```

---

## 🖥️ Personalización Multiplataforma

### Cambio de Fuente
Si los iconos o el texto no se visualizan correctamente en tu sistema (especialmente en Linux/Wayland), puedes cambiar la fuente global al final de `main.py`:

```python
# Busca esta línea en el bloque final
font = QFont("Tu-Fuente-Preferida", 10) # Ej: "Ubuntu", "JetBrains Mono"
app.setFont(font)
```

---

## 🔧 Solución de Problemas (Troubleshooting)

### Configuración del Micrófono
[cite_start]El sistema está configurado para usar el dispositivo de audio con **índice 8**[cite: 1]. Si el programa no detecta tu voz, sigue estos pasos:

1.  Ejecuta el siguiente comando en tu terminal de Python para listar tus dispositivos:
    ```python
    import sounddevice as sd
    print(sd.query_devices())
    ```
2.  Identifica el número de ID de tu micrófono y actualízalo en la primera línea de `Record.py`:
    ```python
    [cite_start]sd.default.device = TU_ID_DETECTADO  # Reemplaza el 8 [cite: 1]
    ```

---

## 📂 Arquitectura del Software

| Archivo | Responsabilidad |
| :--- | :--- |
| **`main.py`** | [cite_start]Gestión de la GUI y flujo de hilos[cite: 1]. |
| **`LiveRecorder.py`** | [cite_start]Captura manual de audio mediante streams[cite: 1]. |
| **`Transcriber.py`** | [cite_start]Motor de IA para procesar archivos `.wav`[cite: 1]. |
| **`TextTyper.py`** | [cite_start]Automatización del portapapeles y teclado[cite: 1]. |
| **`Record.py`** | [cite_start]Clase base para validación de niveles de señal[cite: 1]. |

---

**Desarrollado por lucioamarilla** *Proyecto personal*