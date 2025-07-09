import requests
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import os

# --------------------------------------------------------
# CONFIGURACIÓN - LEE VARIABLES DE ENTORNO (desde GitHub Secrets)
# --------------------------------------------------------
AIO_USERNAME = os.getenv("AIO_USERNAME")
AIO_KEY = os.getenv("AIO_KEY")
FEED_TEMP = "temperatura"
FEED_LUZ = "iluminacion"

# Número de datos a usar (últimos 100 por ejemplo)
N = 100

# --------------------------------------------------------
# FUNCIÓN: descarga datos desde feed de Adafruit IO
# --------------------------------------------------------
def obtener_feed(feed):
    url = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{feed}/data?limit={N}"
    headers = {
        'X-AIO-Key': AIO_KEY,
        'User-Agent': 'iot-informe-bolivia/1.0'
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(f"Error {r.status_code} al acceder al feed '{feed}': {r.text}")
    return r.json()

# --------------------------------------------------------
# OBTENER DATOS DE TEMPERATURA E ILUMINACIÓN
# --------------------------------------------------------
t = obtener_feed(FEED_TEMP)
l = obtener_feed(FEED_LUZ)

# Asegurarse de que tengan igual longitud
n = min(len(t), len(l))

# Crear DataFrame con datos combinados
df = pd.DataFrame({
    "fecha": pd.to_datetime([x['created_at'] for x in t[:n]]),
    "temperatura": [float(x["value"]) for x in t[:n]],
    "iluminacion": [float(x["value"]) for x in l[:n]]
})

# --------------------------------------------------------
# CLUSTERING CON KMEANS (5 CLUSTERS)
# --------------------------------------------------------
scaler = StandardScaler()
X = scaler.fit_transform(df[["temperatura", "iluminacion"]])
kmeans = KMeans(n_clusters=5, random_state=42)
df["cluster"] = kmeans.fit_predict(X)

# Centroides originales
cent = pd.DataFrame(
    scaler.inverse_transform(kmeans.cluster_centers_),
    columns=["temperatura", "iluminacion"]
)

# --------------------------------------------------------
# GRAFICO: CLUSTERS
# --------------------------------------------------------
plt.figure(figsize=(8,6))
for i in range(5):
    grupo = df[df["cluster"] == i]
    plt.scatter(grupo["temperatura"], grupo["iluminacion"], label=f"Patrón {i}")
plt.scatter(cent["temperatura"], cent["iluminacion"], c='black', m
