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
contour_levels = 18
fps = 15   # 10–20 recomendado
duration = int(1000 / fps)  # duración en ms de cada frame

# --- Cargar CSV ---
df = pd.read_csv('datos4.csv')

# --- Normalizar todo el DataFrame a [0,1] ---
df_norm = (df - df.min()) / (df.max() - df.min() + 1e-12)

# --- Crear carpeta de salida (fecha + hora) ---
date_folder = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
project_root = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(project_root, f'seed_{date_folder}')
os.makedirs(output_dir, exist_ok=True)

print(f"📂 Carpeta creada: {output_dir}")

# --- Cuadrícula de coordenadas ---
y = np.linspace(0, 1, H)
x = np.linspace(0, 1, W)
xx, yy = np.meshgrid(x, y)

frames = []

# --- Generar un paisaje por cada fila ---
for idx, row in tqdm(df_norm.iterrows(), total=len(df_norm), desc="Generando paisajes"):
    # Centro controlado por Latitud/Longitud
    cx = row['Latitud']
    cy = row['Longitud']

    # Amplitud controlada por Altitud (entre -1 y 1)
    amp = (row['Altitud'] - 0.5) * 2

    # Dispersión controlada por Ax, Ay
    sigma_x = 0.05 + 0.2 * row['Ax']
    sigma_y = 0.05 + 0.2 * row['Ay']

    # Rotación controlada por Az
    tilt = (row['Az'] - 0.5) * np.pi

    # Transformación de coordenadas
    x_rot = (xx - cx) * np.cos(tilt) - (yy - cy) * np.sin(tilt)
    y_rot = (xx - cx) * np.sin(tilt) + (yy - cy) * np.cos(tilt)

    # Superficie global (una gaussiana deformada)
    z = amp * np.exp(-( (x_rot**2)/(2*sigma_x**2) + (y_rot**2)/(2*sigma_y**2) ))

    # Normalizar para visualización
    zmin, zmax = z.min(), z.max()
    z = (z - zmin) / (zmax - zmin + 1e-12)

    # Graficar
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.set_axis_off()
    ax.imshow(z, cmap='gray_r', origin='lower', extent=(0, 1, 0, 1), interpolation='bilinear')
    levels = np.linspace(0, 1, contour_levels)
    ax.contour(xx, yy, z, levels=levels, colors='black', linewidths=0.6, alpha=0.9, origin='lower')
    ax.set_title(f'Fila {idx+2}', fontsize=8)

    # Guardar PNG
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

print(f"✅ PNGs guardados en: {output_dir}")
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
