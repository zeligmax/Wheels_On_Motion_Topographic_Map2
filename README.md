# Wheels On Motion – Topographic Map 🎶🗺️

**Wheels On Motion – Topographic Map** es la aplicación de escritorio complementaria para el proyecto artístico [Wheels On Motion](https://github.com/zeligmax/Wheels_On_Motion_Windows).

Este proyecto transforma **datos de movimiento de silla de ruedas** (capturados mediante la aplicación Android) en **mapas topográficos dinámicos y animados**, creando visualizaciones generativas basadas en datos reales de sensores.

---

## 📖 Sobre el Proyecto Principal

[Wheels On Motion](https://github.com/zeligmax/Wheels_On_Motion_Windows) es un proyecto artístico que convierte el movimiento de sillas de ruedas en **paisajes sonoros inmersivos**, utilizando técnicas de síntesis de audio y visualización.

Esta aplicación complementaria se centra en la **visualización topográfica**, generando mapas estilizados que responden a los datos de:
- 📍 **GPS**: Latitud, Longitud, Altitud
- 📱 **Acelerómetro**: Ax, Ay, Az

---

## ✨ Características

- 🗺️ **Generación de mapas topográficos dinámicos** basados en datos reales
- 🎬 **Interpolación de frames** para transiciones suaves entre estados
- 📊 **Visualización de datos de sensores** en tiempo real
- 🎨 **Estética minimalista** con curvas de nivel y gradientes
- 💾 **Exportación a GIF animado** para compartir fácilmente
- ⚙️ **Altamente configurable** con parámetros personalizables

---

## 🚀 Instalación

### Requisitos

- Python 3.8+
- Dependencias (instalar con pip):

```bash
pip install numpy pandas matplotlib pillow tqdm
```

### Clonar el repositorio

```bash
git clone https://github.com/tuusuario/Wheels_On_Motion_Topographic_Map2.git
cd Wheels_On_Motion_Topographic_Map2
```

---

## 🎯 Uso

### 1. Preparar tus datos

Necesitas un archivo CSV con el siguiente formato:

```csv
Latitud,Longitud,Altitud,Ax,Ay,Az
41.5359537,2.4487024,55.6,-0.298,5.133,9.662
41.5360123,2.4487156,56.2,-0.301,5.145,9.670
...
```

### 2. Configurar el script

Abre `seed.py` y ajusta el nombre del archivo CSV (líneas 100 y 103):

```python
if not os.path.exists('datos5.csv'):  # Cambia 'datos5.csv' por tu archivo
    ...
df = pd.read_csv('datos5.csv')  # Cambia aquí también
```

### 3. Ejecutar

```bash
python seed.py
```

El script generará:
- 📁 Una carpeta con todas las imágenes individuales
- 🎬 Un archivo GIF animado
- 📊 Visualización opcional en tiempo real

---

## ⚙️ Parámetros Configurables

Puedes ajustar estos parámetros en `seed.py` (líneas 12-20):

| Parámetro | Descripción | Valor por defecto |
|-----------|-------------|-------------------|
| `W, H` | Dimensiones de la imagen (píxeles) | `800, 800` |
| `n_hills` | Número de "colinas" en el mapa | `35` |
| `min_sigma, max_sigma` | Rango de suavidad de colinas | `0.03, 0.25` |
| `contrast` | Intensidad del contraste | `1.2` |
| `contour_levels` | Número de curvas de nivel | `18` |
| `fps` | Frames por segundo del GIF | `15` |
| `interp_frames` | Frames de interpolación entre filas | `5` |

### Ajustar interpolación

El parámetro `interp_frames` controla la suavidad de la animación:

```python
interp_frames = 0   # Sin interpolación (animación brusca)
interp_frames = 5   # Interpolación moderada (recomendado)
interp_frames = 10  # Interpolación muy suave (más frames)
```

---

## 🔬 Cómo Funciona

### Arquitectura del Código

El script está dividido en varios componentes principales:

#### 1. **Validación de Datos** (`validate_csv`)
```python
def validate_csv(df):
    """Verifica que el CSV tenga todas las columnas necesarias"""
```

#### 2. **Normalización** (`normalize_value`)
```python
def normalize_value(val, min_val, max_val):
    """Normaliza valores al rango [0, 1] para consistencia"""
```

#### 3. **Interpolación** (`interpolate_rows`)
```python
def interpolate_rows(row1, row2, t):
    """Crea valores intermedios entre dos filas para transiciones suaves"""
```

#### 4. **Generación Topográfica** (`generate_dynamic_topography`)
Esta es la función principal que convierte datos de sensores en topografía:

```python
def generate_dynamic_topography(row, df_stats, W, H, n_hills, rng):
    """
    Genera un mapa topográfico basado en datos de sensores

    Mapeo de datos:
    - Ax, Ay → Inclinación del terreno (gradiente base)
    - Az → Intensidad de ondulaciones y rugosidad
    - Altitud → Nivel base del terreno y amplitud de colinas
    """
```

### Mapeo de Datos a Visualización

| Dato del Sensor | Efecto Visual |
|----------------|---------------|
| **Ax, Ay** | Controlan la inclinación general del terreno y la posición de las colinas |
| **Az** | Ajusta la intensidad de las ondulaciones (terreno más o menos accidentado) |
| **Altitud** | Define el nivel base del mapa y la amplitud de las elevaciones |

### Proceso de Generación

1. **Carga de datos**: Lee el CSV y calcula estadísticas (min/max) para normalización
2. **Normalización**: Convierte todos los valores al rango [0, 1]
3. **Para cada fila del CSV**:
   - Genera un mapa topográfico basado en los datos de sensores
   - Crea N frames interpolados hacia la siguiente fila
   - Aplica curvas de nivel y renderiza la imagen
4. **Exportación**: Combina todos los frames en un GIF animado

### Algoritmo de Topografía

```
Para cada punto (x, y) del mapa:
  1. Aplicar gradiente base según Ax, Ay
  2. Generar N colinas gaussianas:
     - Posición influenciada por Ax, Ay
     - Amplitud influenciada por Az, Altitud
  3. Añadir offset según Altitud
  4. Añadir ruido controlado por Az
  5. Normalizar y aplicar contraste
```

---

## 📁 Estructura del Proyecto

```
Wheels_On_Motion_Topographic_Map2/
├── seed.py                  # Script principal
├── datos5.csv              # Archivo de datos de ejemplo
├── README.md               # Este archivo
├── .gitignore              # Archivos ignorados por git
└── seed_YYYY-MM-DD_HH-MM-SS/  # Carpetas de salida generadas
    ├── frame_0000.png
    ├── frame_0001.png
    ├── ...
    └── animation_YYYY-MM-DD_HH-MM-SS.gif
```

---

## 🎨 Ejemplo de Salida

### Frame Individual
Cada frame muestra:
- Mapa topográfico con curvas de nivel
- Título con número de fila y datos de sensores
- Gradientes basados en datos reales

### GIF Animado
La animación completa muestra:
- Transición suave entre estados
- Evolución del terreno según el movimiento
- Correlación visual con los datos de sensores

---

## 🔧 Personalización Avanzada

### Cambiar el Estilo Visual

**Cambiar el mapa de colores:**
```python
ax.imshow(z, cmap='terrain', ...)  # Prueba: 'viridis', 'plasma', 'terrain', etc.
```

**Ajustar grosor de curvas de nivel:**
```python
ax.contour(..., linewidths=1.2, ...)  # Valor por defecto: 0.6
```

**Cambiar resolución de salida:**
```python
plt.savefig(..., dpi=150, ...)  # Valor por defecto: 300
```

### Optimizar Rendimiento

**Para datasets grandes:**
```python
interp_frames = 0  # Desactivar interpolación
n_hills = 20       # Reducir complejidad
```

**Para máxima calidad:**
```python
W, H = 1200, 1200  # Mayor resolución
contour_levels = 30  # Más detalle
```

---

## 🐛 Solución de Problemas

### Error: "No se encontró el archivo 'datos5.csv'"
**Solución**: Asegúrate de que el archivo CSV esté en la misma carpeta que `seed.py`, o actualiza la ruta en las líneas 100 y 103.

### Error: "Faltan columnas en el CSV"
**Solución**: Verifica que tu CSV tenga exactamente estas columnas:
```
Latitud, Longitud, Altitud, Ax, Ay, Az
```

### La animación es muy lenta
**Solución**: Reduce `interp_frames` o `n_hills` para generar menos frames o simplificar el cálculo.

### Frames demasiado oscuros/claros
**Solución**: Ajusta el parámetro `contrast` (línea 16):
```python
contrast = 1.5  # Más contraste
contrast = 0.8  # Menos contraste
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar el proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -m 'Añade nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es parte de Wheels On Motion y sigue la misma licencia del proyecto principal.

---

## 👤 Autor

Proyecto desarrollado como parte de **Wheels On Motion**.

Para más información sobre el proyecto principal, visita:
- 🌐 [Wheels On Motion (Windows)](https://github.com/zeligmax/Wheels_On_Motion_Windows)

---

## 🙏 Agradecimientos

- Al proyecto Wheels On Motion por la inspiración y el contexto artístico
- A la comunidad de Python por las excelentes bibliotecas de visualización
- A todos los que contribuyen a hacer la tecnología más accesible e inclusiva

---

## 📮 Contacto

Para preguntas, sugerencias o colaboraciones, abre un issue en el repositorio.

---

**Hecho con ❤️ para Wheels On Motion**
