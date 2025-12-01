import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import os
from datetime import datetime

# === 1. Leer archivo CSV ===
df = pd.read_csv("datos0.csv")

# === 2. Extraer columnas relevantes ===
lat = df["Latitud"].values
lon = df["Longitud"].values
alt = df["Altitud"].values

# === TRANSFORMACIÓN DE DATOS PARA REALCE ===
# Magnitud del acelerómetro (añade rugosidad local)
accel_mag = np.sqrt(df["Ax"]**2 + df["Ay"]**2 + df["Az"]**2)

# Amplificar diferencias de altitud (factor ajustable)
alt_amplified = (alt - np.min(alt)) * 5.0  # factor de amplificación

# Añadir rugosidad del acelerómetro (factor ajustable)
alt_rugged = alt_amplified + 0.5 * (accel_mag - np.mean(accel_mag))

# Normalización no lineal para resaltar relieves pequeños
alt_final = np.sign(alt_rugged) * np.abs(alt_rugged) ** 1.2

# Usar alt_final para la interpolación
alt = alt_final

# === 3. Comprobar cuántos puntos hay y si los datos son "planos" ===
def is_flat(coords, tol=1e-4):
    # Comprueba si la dispersión de los datos es demasiado pequeña
    return (np.ptp(coords[0]) < tol) or (np.ptp(coords[1]) < tol)

if len(df) < 4 or is_flat((lat, lon)):
    print("⚠️ Pocos puntos o datos casi idénticos en lat/lon. Generando relieve simulado...")

    # Crear una malla en torno al único punto
    grid_x, grid_y = np.mgrid[lat[0]-1:lat[0]+1:200j, lon[0]-1:lon[0]+1:200j]

    # Gaussiana centrada en el punto
    grid_z = np.exp(-((grid_x - lat[0])**2 + (grid_y - lon[0])**2) / 0.01) * alt[0]

else:
    # Crear malla regular basada en todos los puntos
    grid_x, grid_y = np.mgrid[min(lat):max(lat):200j, min(lon):max(lon):200j]

    try:
        # Interpolación cúbica
        grid_z = griddata((lat, lon), alt, (grid_x, grid_y), method="cubic")
    except Exception as e:
        print(f"⚠️ Error en la interpolación: {e}\nGenerando relieve simulado...")
        grid_z = np.exp(-((grid_x - lat[0])**2 + (grid_y - lon[0])**2) / 0.01) * alt[0]


# === 4. Visualización mejorada estilo other.py ===
# Normalizar y aumentar contraste
contrast = 1.2  # igual que en other.py
z = grid_z.copy()
z = np.nan_to_num(z, nan=np.nanmin(z))  # reemplaza NaN por el mínimo
zmin, zmax = z.min(), z.max()
z = (z - zmin) / (zmax - zmin + 1e-12)
z = np.clip((z - 0.5) * contrast + 0.5, 0, 1)

# Añadir un poco de ruido para textura
noise_level = 0.08
rng = np.random.default_rng(int(datetime.utcnow().timestamp() * 1000) % (2**32 - 1))
z += noise_level * rng.standard_normal(size=z.shape)
z = np.clip(z, 0, 1)

fig, ax = plt.subplots(figsize=(6,6), dpi=150)
ax.set_axis_off()

# Sombreado en grises (zonas altas más oscuras)
ax.imshow(z, cmap='gray_r', origin='lower', extent=(grid_y.min(), grid_y.max(), grid_x.min(), grid_x.max()), interpolation='bilinear')

# Líneas de contorno negras
contour_levels = 18
levels = np.linspace(0, 1, contour_levels)
ax.contour(grid_x, grid_y, z, levels=levels, colors='black', linewidths=0.6, alpha=0.9, origin='lower')

plt.tight_layout()

# === 5. Guardar imagen en la carpeta actual con fecha/hora ===
output_dir = os.path.dirname(os.path.abspath(__file__))
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = os.path.join(output_dir, f"mapa_topografico_{timestamp}.png")

plt.savefig(output_file, dpi=300, bbox_inches="tight", pad_inches=0)
plt.show()

print(f"✅ Mapa guardado en: {output_file}")

