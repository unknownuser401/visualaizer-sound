import numpy as np
import pygame
import pyaudio

# Configuración de Pygame
pygame.init()
width, height = 800, 400
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Audio Visualizer')

# Configuración de PyAudio
p = pyaudio.PyAudio()
samplerate = 44100
chunk_size = 1024

# Configuración del visualizador
fps = 30
clock = pygame.time.Clock()
line_color = (255, 255, 255)
max_amplitude = 32767  # Valor máximo para normalización

# Definir variables para almacenar la forma de onda
x_values = np.linspace(0, width, chunk_size, endpoint=False)
y_values = np.zeros_like(x_values)

def audio_callback(in_data, frame_count, time_info, status):
    # Obtener amplitud del audio
    data = np.frombuffer(in_data, dtype=np.int16)
    
    # Normalizar y ajustar la escala
    normalized_data = data / max_amplitude

    # Ajustar las dimensiones de y_values
    if len(normalized_data) < len(y_values):
        y_values[:len(normalized_data)] = normalized_data * (height / 2) + height / 2
        y_values[len(normalized_data):] = 0
    else:
        y_values[:] = normalized_data[:len(y_values)] * (height / 2) + height / 2

    return (in_data, pyaudio.paContinue)

# Configurar el dispositivo de audio (utilizando el dispositivo predeterminado)
stream = p.open(format=pyaudio.paInt16,
                channels=2,
                rate=samplerate,
                input=True,
                stream_callback=audio_callback,
                frames_per_buffer=chunk_size)

# Iniciar la transmisión de audio
stream.start_stream()

# Bucle principal de Pygame
while stream.is_active():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            stream.stop_stream()
            stream.close()
            p.terminate()
            raise SystemExit

    # Dibujar la forma de onda
    window.fill((0, 0, 0))
    pygame.draw.lines(window, line_color, False, list(zip(x_values, y_values)), 2)

    pygame.display.flip()
    clock.tick(fps)

# Detener la transmisión y cerrar los objetos PyAudio
stream.stop_stream()
stream.close()
p.terminate()
