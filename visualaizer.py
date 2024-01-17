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
bar_width = 5
bar_spacing = 2
num_bars = width // (bar_width + bar_spacing)
bars_left = [0] * num_bars
bars_right = [0] * num_bars

def audio_callback(in_data, frame_count, time_info, status):
    # Obtener amplitud del audio
    data = np.frombuffer(in_data, dtype=np.int16)
    left_data = data[0::2]
    right_data = data[1::2]
    
    spectrum_left = np.abs(np.fft.fft(left_data))
    spectrum_right = np.abs(np.fft.fft(right_data))
    spectrum_left = spectrum_left[:num_bars]
    spectrum_right = spectrum_right[:num_bars]

    # Normalizar y ajustar la escala
    spectrum_left /= spectrum_left.max()
    spectrum_right /= spectrum_right.max()
    
    bars_left[:] = spectrum_left * height
    bars_right[:] = spectrum_right * height

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

    # Dibujar el visualizador
    window.fill((0, 0, 0))
    for i in range(num_bars):
        x = i * (bar_width + bar_spacing)
        pygame.draw.rect(window, (255, 0, 0), (x, height - bars_left[i], bar_width, bars_left[i]))
        pygame.draw.rect(window, (0, 0, 255), (x, height - bars_right[i], bar_width, bars_right[i]))

    pygame.display.flip()
    clock.tick(fps)

# Detener la transmisión y cerrar los objetos PyAudio
stream.stop_stream()
stream.close()
p.terminate()
