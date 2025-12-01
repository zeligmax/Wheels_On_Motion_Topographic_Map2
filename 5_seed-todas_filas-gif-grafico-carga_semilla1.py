import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from tqdm import tqdm
from PIL import Image

# --- Parámetros ---
cols = ['Latitud', 'Longitud', 'Altitud', 'Ax', 'Ay', 'Az']
W, H = 800, 800
n_hills = 35
min_sigma, max_sigma = 0.03, 0.25
contrast = 1.2
contour_levels = 18
fps = 15  # <- Cambia esto (10-20 recomendado)
duration = int(1000 / fps)  # duración de cada frame en ms

# --- Cargar datos ---
df = pd.read_csv('datos6.csv')

# --- Crear carpeta de salida (fecha + hora) ---
date_folder = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
project_root = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(project_root, f'seed_{date_folder}')
os.makedirs(output_dir, exist_ok=True)

print(f"📂 Carpeta creada: {output_dir}")

# --- Calcular la semilla una sola vez con la primera fila ---
first_row = df.iloc[0]
seed_val = int((first_row['Latitud'] + first_row['Longitud'] + first_row['Altitud']) * 1e6) % (2**32 - 1)
rng = np.random.default_rng(seed_val)

# --- Generar imágenes ---
frames = []
for idx, row in tqdm(df.iterrows(), total=len(df), desc="Generando imágenes"):

    y = np.linspace(0, 1, H)
    x = np.linspace(0, 1, W)
    xx, yy = np.meshgrid(x, y)
    z = np.zeros_like(xx)

    for _ in range(n_hills):
        cx = rng.random()
        cy = rng.random()
        amp = rng.uniform(-1.0, 1.0) * rng.uniform(0.4, 1.0)
        sigma = rng.uniform(min_sigma, max_sigma)
        g = amp * np.exp(-((xx - cx)**2 + (yy - cy)**2) / (2 * sigma**2))
        z += g

    z += 0.08 * rng.standard_normal(size=z.shape)
    zmin, zmax = z.min(), z.max()
    z = (z - zmin) / (zmax - zmin + 1e-12)
    z = np.clip((z - 0.5) * contrast + 0.5, 0, 1)

    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.set_axis_off()
    ax.imshow(z, cmap='gray_r', origin='lower', extent=(0, 1, 0, 1), interpolation='bilinear')
    levels = np.linspace(0, 1, contour_levels)
    ax.contour(xx, yy, z, levels=levels, colors='black', linewidths=0.6, alpha=0.9, origin='lower')
    ax.set_title(f'Fila {idx+2} (semilla fija: {seed_val})', fontsize=8)

    output_file = os.path.join(output_dir, f"frame_{idx:04d}.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

    frames.append(Image.open(output_file))

# --- Crear GIF ---
gif_path = os.path.join(output_dir, f"animation_{date_folder}.gif")
frames[0].save(
    gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=duration,
    loop=0
)

print(f"✅ Imágenes guardadas en: {output_dir}")
print(f"✅ GIF creado en: {gif_path}")

# --- Preguntar si visualizar ---
ver = input("¿Quieres visualizar la animación ahora? (s/n): ").strip().lower()
if ver == "s":
    import matplotlib.animation as animation

    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.set_axis_off()

    img_plot = ax.imshow(np.zeros((H, W)), cmap='gray_r', origin='lower')

    def update(i):
        frame = np.array(frames[i])
        img_plot.set_data(frame)
        return [img_plot]

    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=duration, blit=True)
    plt.show()
