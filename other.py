import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Parámetros
W, H = 800, 800        # tamaño de la imagen en píxeles
n_hills = 35           # número de "colinas" gaussianas
min_sigma, max_sigma = 0.03, 0.25  # tamaño de las colinas (relativo a la imagen)
contrast = 1.2         # mayor contraste -> relieve más marcado
contour_levels = 18    # número de curvas de nivel

# Semilla aleatoria basada en la hora actual (cada ejecución es distinta)
seed = int(datetime.utcnow().timestamp() * 1000) % (2**32 - 1)
rng = np.random.default_rng(seed)

# Crear la cuadrícula
y = np.linspace(0, 1, H)
x = np.linspace(0, 1, W)
xx, yy = np.meshgrid(x, y)

# Construir el campo de altura sumando "colinas" gaussianas
z = np.zeros_like(xx)
for _ in range(n_hills):
    cx = rng.random()  # centro en x
    cy = rng.random()  # centro en y
    amp = rng.uniform(-1.0, 1.0) * rng.uniform(0.4, 1.0)  # amplitud (puede ser negativa)
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

# Sombreado en grises (zonas altas más oscuras)
ax.imshow(z, cmap='gray_r', origin='lower', extent=(0,1,0,1), interpolation='bilinear')

# Líneas de contorno negras
levels = np.linspace(0, 1, contour_levels)
ax.contour(xx, yy, z, levels=levels, colors='black', linewidths=0.6, alpha=0.9, origin='lower')

# Ajustar y guardar imagen automáticamente en la carpeta actual
plt.tight_layout()

# Guardar imagen con nombre 'other_<fecha-hora>.png' en la carpeta actual
from datetime import datetime
import os
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_dir, f"other_{timestamp}.png")
plt.savefig(output_file, dpi=300, bbox_inches="tight", pad_inches=0)
plt.show()

print(f"Mapa generado con semilla: {seed}")
print(f"✅ Imagen guardada en: {output_file}")
