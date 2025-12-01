import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from PIL import Image  # Para crear el GIF

# Leer el CSV
df = pd.read_csv('datos0.csv')

# Parámetros
cols = ['Latitud', 'Longitud', 'Altitud', 'Ax', 'Ay', 'Az']
W, H = 800, 800
n_hills = 35
min_sigma, max_sigma = 0.03, 0.25
contrast = 1.2
contour_levels = 18

# FPS deseados para el GIF
fps = 15   # Cambia este valor a 10, 15 o 20
duration = int(1000 / fps)  # duración en ms por frame

# Carpeta de salida en la raíz del proyecto
date_folder = datetime.now().strftime('%Y-%m-%d')
project_root = os.path.dirname(os.path.abspath(__file__))  # raíz del proyecto
output_dir = os.path.join(project_root, f'seed_{date_folder}')
os.makedirs(output_dir, exist_ok=True)

plt.ion()  # modo interactivo
fig, ax = plt.subplots(figsize=(6,6), dpi=150)

# Lista de imágenes guardadas para el GIF
saved_images = []

for idx, row in df.iterrows():
    # Semilla desde los datos
    seed_val = int(np.sum([row[c] for c in cols]) * 1e6) % (2**32 - 1)
    rng = np.random.default_rng(seed_val)

    # Crear grid
    y = np.linspace(0, 1, H)
    x = np.linspace(0, 1, W)
    xx, yy = np.meshgrid(x, y)

    # Generar colinas
    z = np.zeros_like(xx)
    for _ in range(n_hills):
        cx = rng.random()
        cy = rng.random()
        amp = rng.uniform(-1.0, 1.0) * rng.uniform(0.4, 1.0)
        sigma = rng.uniform(min_sigma, max_sigma)
        g = amp * np.exp(-((xx - cx)**2 + (yy - cy)**2) / (2 * sigma**2))
        z += g

    # Ruido + normalización
    z += 0.08 * rng.standard_normal(size=z.shape)
    zmin, zmax = z.min(), z.max()
    z = (z - zmin) / (zmax - zmin + 1e-12)
    z = np.clip((z - 0.5) * contrast + 0.5, 0, 1)

    # Graficar
    ax.clear()
    ax.set_axis_off()
    ax.imshow(z, cmap='gray_r', origin='lower', extent=(0,1,0,1), interpolation='bilinear')
    levels = np.linspace(0, 1, contour_levels)
    ax.contour(xx, yy, z, levels=levels, colors='black', linewidths=0.6, alpha=0.9, origin='lower')
    ax.set_title(f'Fila {idx+1} (semilla: {seed_val})', fontsize=10)
    plt.tight_layout()
    plt.pause(0.01)  # Pausa mínima, solo para refrescar animación

    # Guardar cada imagen
    timestamp = datetime.now().strftime('%H-%M-%S-%f')
    output_file = os.path.join(output_dir, f'fila_{idx+1}_seed_{seed_val}_{timestamp}.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0)
    saved_images.append(output_file)

plt.ioff()

# Crear GIF con todas las imágenes
gif_path = os.path.join(output_dir, f'animacion_seed_{date_folder}_{fps}fps.gif')
frames = [Image.open(img) for img in saved_images]
frames[0].save(
    gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=duration,  # velocidad según FPS
    loop=0
)

print(f"✅ Todas las imágenes guardadas en: {output_dir}")
print(f"✅ GIF creado en: {gif_path} ({fps} FPS)")
