import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Leer el CSV (sin usar Timestamp para la semilla)
df = pd.read_csv('datos0.csv')

# Calcular la semilla solo a partir de la primera fila de datos (segunda línea del CSV)
cols = ['Latitud', 'Longitud', 'Altitud', 'Ax', 'Ay', 'Az']
row = df.iloc[0]
seed_val = int(np.sum([row[c] for c in cols]) * 1e6) % (2**32 - 1)

# Parámetros visuales
W, H = 800, 800
n_hills = 35
min_sigma, max_sigma = 0.03, 0.25
contrast = 1.2
contour_levels = 18

# Inicializar generador aleatorio con la semilla calculada
txt_seed = f"Semilla generada a partir de datos0.csv: {seed_val}"
rng = np.random.default_rng(seed_val)

# Crear la cuadrícula
y = np.linspace(0, 1, H)
x = np.linspace(0, 1, W)
xx, yy = np.meshgrid(x, y)

# Construir el campo de altura sumando "colinas" gaussianas
z = np.zeros_like(xx)
for _ in range(n_hills):
    cx = rng.random()
    cy = rng.random()
    amp = rng.uniform(-1.0, 1.0) * rng.uniform(0.4, 1.0)
    sigma = rng.uniform(min_sigma, max_sigma)
    g = amp * np.exp(-((xx - cx)**2 + (yy - cy)**2) / (2 * sigma**2))
    z += g

# Añadir un poco de ruido para textura
z += 0.08 * rng.standard_normal(size=z.shape)

# Normalizar y aumentar contraste
zmin, zmax = z.min(), z.max()
z = (z - zmin) / (zmax - zmin + 1e-12)
z = np.clip((z - 0.5) * contrast + 0.5, 0, 1)

# Graficar: escala de grises + curvas de nivel negras
fig, ax = plt.subplots(figsize=(6,6), dpi=150)
ax.set_axis_off()
ax.imshow(z, cmap='gray_r', origin='lower', extent=(0,1,0,1), interpolation='bilinear')
levels = np.linspace(0, 1, contour_levels)
ax.contour(xx, yy, z, levels=levels, colors='black', linewidths=0.6, alpha=0.9, origin='lower')
plt.tight_layout()

# Guardar imagen en la carpeta actual con nombre 'seed_<fecha-hora>.png'
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
output_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_dir, f'seed_{timestamp}.png')
plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0)
plt.show()

print(txt_seed)
print(f'✅ Imagen guardada en: {output_file}')
