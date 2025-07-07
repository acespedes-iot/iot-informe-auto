import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import os

# Leer credenciales desde variables de entorno
AIO_USERNAME = os.getenv("AIO_USERNAME")
AIO_KEY = os.getenv("AIO_KEY")
FEED_TEMP = "temperatura"
FEED_LUZ = "iluminacion"

# Función para obtener datos del feed
def obtener_feed(feed, n=50):
    url = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{feed}/data?limit={n}"
    headers = {
        "X-AIO-Key": AIO_KEY,
        "User-Agent": "iot-informe-github/1.0"
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(f"Error {r.status_code} al acceder al feed '{feed}': {r.text}")
    return r.json()

# Obtener datos
t = obtener_feed(FEED_TEMP)
l = obtener_feed(FEED_LUZ)
n = min(len(t), len(l))

df = pd.DataFrame({
    "fecha": pd.to_datetime([x['created_at'] for x in t[:n]]),
    "temperatura": [float(x['value']) for x in t[:n]],
    "iluminacion": [float(x['value']) for x in l[:n]]
})

# Análisis de clustering
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[["temperatura", "iluminacion"]])
kmeans = KMeans(n_clusters=3, random_state=42)
df["cluster"] = kmeans.fit_predict(X_scaled)

# Tendencias
df_sorted = df.sort_values("fecha")
df_sorted["media_movil_temp"] = df_sorted["temperatura"].rolling(window=5).mean()
df_sorted["media_movil_luz"] = df_sorted["iluminacion"].rolling(window=5).mean()

# Graficar
plt.figure(figsize=(10, 4))
plt.plot(df_sorted["fecha"], df_sorted["media_movil_temp"], label="Tendencia Temperatura")
plt.plot(df_sorted["fecha"], df_sorted["media_movil_luz"], label="Tendencia Iluminación")
plt.legend()
plt.title("Tendencias")
plt.xlabel("Fecha")
plt.ylabel("Valor")
plt.tight_layout()
plt.savefig("tendencia.png")
plt.close()

plt.figure(figsize=(6, 5))
plt.scatter(df["temperatura"], df["iluminacion"], c=df["cluster"], cmap="viridis")
plt.xlabel("Temperatura")
plt.ylabel("Iluminación")
plt.title("Clusters")
plt.tight_layout()
plt.savefig("clusters.png")
plt.close()

# Interpretación simple
interpre = "Se identificaron 3 patrones distintos de comportamiento en temperatura e iluminación."

# Crear HTML
with open("informe.html", "w") as f:
    f.write(f"""
    <html>
    <head><title>Informe IoT</title></head>
    <body>
    <h1>Informe de Comportamiento - Temperatura e Iluminación</h1>
    <h2>Tendencias</h2>
    <img src='tendencia.png' width='600'><br>
    <h2>Clusters</h2>
    <img src='clusters.png' width='600'><br>
    <h2>Interpretación</h2>
    <p>{interpre}</p>
    <p><i>Generado automáticamente por IA desde GitHub Actions</i></p>
    </body>
    </html>
    """)

