import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from tqdm import tqdm
from PIL import Image
import io
import sys

# --- Parámetros ---
REQUIRED_COLS = ['Latitud', 'Longitud', 'Altitud', 'Ax', 'Ay', 'Az']
W, H = 800, 800
n_hills = 35
min_sigma, max_sigma = 0.03, 0.25
contrast = 1.2
contour_levels = 18
fps = 15
duration = int(1000 / fps)
interp_frames = 5  # Número de frames intermedios entre cada par de filas (0 = sin interpolación)

def validate_csv(df):
    """Valida que el CSV tenga las columnas requeridas"""
    missing_cols = [col for col in REQUIRED_COLS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Faltan columnas en el CSV: {missing_cols}")
    if len(df) == 0:
        raise ValueError("El CSV está vacío")
    return True

def normalize_value(val, min_val, max_val):
    """Normaliza un valor al rango [0, 1]"""
    if max_val - min_val == 0:
        return 0.5
    return (val - min_val) / (max_val - min_val)

def interpolate_rows(row1, row2, t):
    """
    Interpola entre dos filas del dataframe

    Args:
        row1: Primera fila
        row2: Segunda fila
        t: Factor de interpolación [0, 1], donde 0=row1 y 1=row2

    Returns:
        Serie de pandas con valores interpolados
    """
    interpolated = row1.copy()
    for col in REQUIRED_COLS:
        interpolated[col] = row1[col] * (1 - t) + row2[col] * t
    return interpolated

def generate_dynamic_topography(row, df_stats, W, H, n_hills, rng):
    """
    Genera topografía dinámica basada en datos del acelerómetro y altitud

    Args:
        row: Fila actual con datos de sensores
        df_stats: Estadísticas del dataframe (min/max para normalización)
        W, H: Dimensiones de la imagen
        n_hills: Número de colinas a generar
        rng: Generador de números aleatorios
    """
    y = np.linspace(0, 1, H)
    x = np.linspace(0, 1, W)
    xx, yy = np.meshgrid(x, y)
    z = np.zeros_like(xx)

    # Normalizar valores del acelerómetro
    ax_norm = normalize_value(row['Ax'], df_stats['Ax']['min'], df_stats['Ax']['max'])
    ay_norm = normalize_value(row['Ay'], df_stats['Ay']['min'], df_stats['Ay']['max'])
    az_norm = normalize_value(row['Az'], df_stats['Az']['min'], df_stats['Az']['max'])
    alt_norm = normalize_value(row['Altitud'], df_stats['Altitud']['min'], df_stats['Altitud']['max'])

    # Usar Ax, Ay para crear un gradiente base (inclinación del terreno)
    # Escalamos al rango [-1, 1] para tener pendientes en ambas direcciones
    ax_scaled = (ax_norm - 0.5) * 2
    ay_scaled = (ay_norm - 0.5) * 2

    # Gradiente base del terreno basado en acelerómetro
    base_gradient = ax_scaled * xx + ay_scaled * yy
    z += base_gradient * 0.3

    # Usar Az para controlar la intensidad de las ondulaciones
    az_intensity = 0.3 + az_norm * 1.2  # Rango [0.3, 1.5]

    # Generar colinas con posiciones y características influenciadas por los datos
    for _ in range(n_hills):
        # Posición de las colinas sesgada por Ax, Ay
        cx = rng.random() * 0.6 + ax_norm * 0.4
        cy = rng.random() * 0.6 + ay_norm * 0.4

        # Amplitud influenciada por Az y altitud
        base_amp = rng.uniform(-1.0, 1.0) * rng.uniform(0.4, 1.0)
        amp = base_amp * az_intensity * (0.7 + alt_norm * 0.6)

        sigma = rng.uniform(min_sigma, max_sigma)
        g = amp * np.exp(-((xx - cx)**2 + (yy - cy)**2) / (2 * sigma**2))
        z += g

    # Añadir offset basado en altitud
    z += (alt_norm - 0.5) * 0.4

    # Ruido controlado por Az
    noise_level = 0.05 + az_norm * 0.06
    z += noise_level * rng.standard_normal(size=z.shape)

    # Normalizar y aplicar contraste
    zmin, zmax = z.min(), z.max()
    z = (z - zmin) / (zmax - zmin + 1e-12)
    z = np.clip((z - 0.5) * contrast + 0.5, 0, 1)

    return z, xx, yy

try:
    # --- Cargar datos ---
    if not os.path.exists('datos5.csv'):
        raise FileNotFoundError("No se encontró el archivo 'datos5.csv'")

    df = pd.read_csv('datos5.csv')
    validate_csv(df)

    # Calcular estadísticas para normalización
    df_stats = {
        'Ax': {'min': df['Ax'].min(), 'max': df['Ax'].max()},
        'Ay': {'min': df['Ay'].min(), 'max': df['Ay'].max()},
        'Az': {'min': df['Az'].min(), 'max': df['Az'].max()},
        'Altitud': {'min': df['Altitud'].min(), 'max': df['Altitud'].max()}
    }

    # --- Crear carpeta de salida (fecha + hora) ---
    date_folder = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_root, f'seed_{date_folder}')
    os.makedirs(output_dir, exist_ok=True)

    print(f"📂 Carpeta creada: {output_dir}")

    # Calcular total de frames con interpolación
    total_frames = len(df) + (len(df) - 1) * interp_frames
    print(f"📊 Generando {total_frames} mapas topográficos dinámicos...")
    print(f"   ({len(df)} filas originales + {(len(df) - 1) * interp_frames} frames interpolados)")

    # --- Generar imágenes ---
    frames = []
    frame_counter = 0

    with tqdm(total=total_frames, desc="Generando imágenes") as pbar:
        for idx in range(len(df)):
            row = df.iloc[idx]

            # Generar frame para la fila actual
            seed_val = int(np.sum([row[c] for c in REQUIRED_COLS]) * 1e6) % (2**32 - 1)
            rng = np.random.default_rng(seed_val)
            z, xx, yy = generate_dynamic_topography(row, df_stats, W, H, n_hills, rng)

            # Crear figura
            fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
            ax.set_axis_off()
            ax.imshow(z, cmap='gray_r', origin='lower', extent=(0, 1, 0, 1), interpolation='bilinear')
            levels = np.linspace(0, 1, contour_levels)
            ax.contour(xx, yy, z, levels=levels, colors='black', linewidths=0.6, alpha=0.9, origin='lower')

            # Título con información de sensores
            title = (f'Fila {idx+1} | Alt: {row["Altitud"]:.1f}m | '
                    f'Accel: ({row["Ax"]:.2f}, {row["Ay"]:.2f}, {row["Az"]:.2f})')
            ax.set_title(title, fontsize=7)

            # Guardar frame en archivo
            output_file = os.path.join(output_dir, f"frame_{frame_counter:04d}.png")
            plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0)

            # Guardar frame en memoria para el GIF
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
            buf.seek(0)
            frames.append(Image.open(buf).copy())
            buf.close()
            plt.close(fig)

            frame_counter += 1
            pbar.update(1)

            # Generar frames interpolados hacia la siguiente fila
            if idx < len(df) - 1 and interp_frames > 0:
                next_row = df.iloc[idx + 1]

                for i in range(1, interp_frames + 1):
                    t = i / (interp_frames + 1)  # Factor de interpolación
                    interp_row = interpolate_rows(row, next_row, t)

                    # Generar frame interpolado
                    seed_val = int(np.sum([interp_row[c] for c in REQUIRED_COLS]) * 1e6) % (2**32 - 1)
                    rng = np.random.default_rng(seed_val)
                    z, xx, yy = generate_dynamic_topography(interp_row, df_stats, W, H, n_hills, rng)

                    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
                    ax.set_axis_off()
                    ax.imshow(z, cmap='gray_r', origin='lower', extent=(0, 1, 0, 1), interpolation='bilinear')
                    levels = np.linspace(0, 1, contour_levels)
                    ax.contour(xx, yy, z, levels=levels, colors='black', linewidths=0.6, alpha=0.9, origin='lower')

                    # Título para frame interpolado
                    title = (f'Fila {idx+1}→{idx+2} ({t*100:.0f}%) | Alt: {interp_row["Altitud"]:.1f}m | '
                            f'Accel: ({interp_row["Ax"]:.2f}, {interp_row["Ay"]:.2f}, {interp_row["Az"]:.2f})')
                    ax.set_title(title, fontsize=7)

                    # Guardar frame interpolado
                    output_file = os.path.join(output_dir, f"frame_{frame_counter:04d}.png")
                    plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0)

                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
                    buf.seek(0)
                    frames.append(Image.open(buf).copy())
                    buf.close()
                    plt.close(fig)

                    frame_counter += 1
                    pbar.update(1)

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

except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
except ValueError as e:
    print(f"❌ Error de validación: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1)
