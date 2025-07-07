# ✅ OPCIÓN 2: SOLUCIÓN SEMIAUTOMÁTICA - IoT + IA + ADAFRUIT IO
# Autor: ChatGPT - Adaptado para Alexander
# Ejemplo con variables: TEMPERATURA e ILUMINACIÓN en granjas de pollo

# -----------------------------------------------------------------------------
# 1️⃣ ENVÍO DE DATOS POR MQTT DESDE SENSOR A ADAFRUIT IO (ESP8266 con Arduino)
# -----------------------------------------------------------------------------
# Código no incluido aquí por estar ya desarrollado previamente

# -----------------------------------------------------------------------------
# 2️⃣ ENTRENAMIENTO PREVIO EN GOOGLE COLAB Y CREACIÓN DEL .PKL
# -----------------------------------------------------------------------------
# Ya está documentado anteriormente y se ejecuta en Google Colab una vez con CSVs

# -----------------------------------------------------------------------------
# 3️⃣ main.py — LECTURA, ANÁLISIS, INTERPRETACIÓN Y REPORTE HTML CON GRÁFICOS
# -----------------------------------------------------------------------------

import requests
import pandas as pd
import joblib
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import os

# ⚙️ Configuración Adafruit
AIO_USERNAME = os.getenv("AIO_USERNAME")
AIO_KEY = os.getenv("AIO_KEY")
FEED_TEMPERATURA = 'temperatura'
FEED_ILUMINACION = 'iluminacion'

HEADERS = {
    'X-AIO-Key': AIO_KEY,
    'User-Agent': 'iot-informe-bolivia/1.0'
}

# 📥 Descargar datos del feed

def obtener_feed(feed):
    url = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{feed}/data?limit=100"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        raise Exception(f"Error {r.status_code} al acceder al feed '{feed}': {r.text}")
    return r.json()

t = obtener_feed(FEED_TEMPERATURA)
i = obtener_feed(FEED_ILUMINACION)
n = min(len(t), len(i))

# 🧾 Crear DataFrame

df = pd.DataFrame({
    "fecha": pd.to_datetime([x['created_at'] for x in t[:n]]),
    "temperatura": [float(x['value']) for x in t[:n]],
    "iluminacion": [float(x['value']) for x in i[:n]]
})

# 🤖 Clustering y escalamiento

X = df[['temperatura', 'iluminacion']]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
kmeans = KMeans(n_clusters=3, random_state=42)
df['cluster'] = kmeans.fit_predict(X_scaled)
cent = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=['temperatura','iluminacion'])

# 📊 Gráfico de Clústeres
plt.figure()
for c in range(3):
    grupo = df[df['cluster'] == c]
    plt.scatter(grupo['temperatura'], grupo['iluminacion'], label=f'Patrón {c+1}')
plt.xlabel('Temperatura (°C)')
plt.ylabel('Iluminación (lux)')
plt.legend()
plt.title('Agrupación de Comportamientos')
plt.tight_layout()
plt.savefig('clusters.png')

# 📈 Tendencia temporal
plt.figure()
plt.plot(df['fecha'], df['temperatura'], label='Temperatura', color='red')
plt.plot(df['fecha'], df['iluminacion'], label='Iluminación', color='blue')
plt.xlabel('Fecha')
plt.ylabel('Valor')
plt.title('Tendencias Recientes')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('tendencia.png')

# 🔍 Interpretación detallada
interpretaciones = []
for idx, row in cent.iterrows():
    temp, ilum = row['temperatura'], row['iluminacion']
    interp = f"🔹 <b>Patrón {idx+1}</b>: Temperatura ~{temp:.1f}°C, Iluminación ~{ilum:.0f} lux. "
    if temp > 29 and ilum > 400:
        interp += "⚠️ Riesgo de sobrecalentamiento por exposición intensa."
    elif temp < 24 and ilum < 200:
        interp += "🌙 Ambientes fríos y oscuros, típicos de la noche."
    elif 25 <= temp <= 28 and 200 <= ilum <= 350:
        interp += "✅ Condiciones ideales de confort térmico."
    else:
        interp += "ℹ️ Combinación atípica, requiere seguimiento."
    interpretaciones.append(interp)

# 📝 Informe HTML
html = f"""
<html><head><meta charset='utf-8'><title>Informe IoT</title></head><body>
<h1>📊 Informe Automático IoT</h1>
<p>📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<h2>📌 Análisis de Clústeres</h2>
<img src='clusters.png' width='600'><br><br>
<ul>{''.join([f'<li>{x}</li>' for x in interpretaciones])}</ul>
<h2>📈 Tendencias</h2>
<img src='tendencia.png' width='600'>
</body></html>
"""

with open('informe.html', 'w') as f:
    f.write(html)

print("✅ Informe generado correctamente")
