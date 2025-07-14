# ✅ OPCIÓN 2: SOLUCIÓN SEMIAUTOMÁTICA - IoT + IA + ADAFRUIT IO
# Autor: ChatGPT - Adaptado para Alexander
# Ejemplo con variables: TEMPERATURA e ILUMINACIÓN en granjas de pollo

import requests
import pandas as pd
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
cent = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=['temperatura', 'iluminacion'])

# 🎨 Colores consistentes
colores_patron = ['red', 'blue', 'green']

# 📊 Gráfico de Clústeres
plt.figure()
for c in range(3):
    grupo = df[df['cluster'] == c]
    plt.scatter(grupo['temperatura'], grupo['iluminacion'], color=colores_patron[c], label=f'Patrón {c+1}')
plt.xlabel('Temperatura (°C)')
plt.ylabel('Iluminación (lux)')
plt.legend()
plt.title('Agrupación de Comportamientos')
plt.tight_layout()
plt.savefig('clusters.png')

# 📈 Tendencia temporal con dos ejes Y
fig, ax1 = plt.subplots()
color_temp = 'tab:red'
color_ilum = 'tab:blue'

ax1.set_xlabel('Fecha')
ax1.set_ylabel('Temperatura (°C)', color=color_temp)
ax1.plot(df['fecha'], df['temperatura'], color=color_temp, label='Temperatura')
ax1.tick_params(axis='y', labelcolor=color_temp)

ax2 = ax1.twinx()
ax2.set_ylabel('Iluminación (lux)', color=color_ilum)
ax2.plot(df['fecha'], df['iluminacion'], color=color_ilum, label='Iluminación')
ax2.tick_params(axis='y', labelcolor=color_ilum)

fig.autofmt_xdate()
plt.title('Tendencias Recientes')
fig.tight_layout()
plt.savefig('tendencia.png')

# 🔍 Interpretación detallada
interpretaciones = []
for idx, row in cent.iterrows():
    temp, ilum = row['temperatura'], row['iluminacion']
    color = colores_patron[idx]
    interp = f"<li><span style='color:{color}'>🔹 <b>Patrón {idx+1}</b>: Temperatura ~{temp:.1f}°C, Iluminación ~{ilum:.0f} lux. "
    if temp > 29 and ilum > 400:
        interp += "⚠️ Riesgo de sobrecalentamiento por exposición intensa."
    elif temp < 24 and ilum < 200:
        interp += "🌙 Ambientes fríos y oscuros, típicos de la noche."
    elif 25 <= temp <= 28 and 200 <= ilum <= 350:
        interp += "✅ Condiciones ideales de confort térmico."
    else:
        interp += "ℹ️ Combinación atípica, requiere seguimiento."
    interp += "</span></li>"
    interpretaciones.append(interp)

# 📊 Resumen de conteo por clúster
conteos = df['cluster'].value_counts().sort_index()
resumen = "<h3>📊 Distribución de patrones:</h3><ul>"
for idx, count in conteos.items():
    resumen += f"<li><span style='color:{colores_patron[idx]}'><b>Patrón {idx+1}</b>: {count} muestras</span></li>"
resumen += "</ul>"

# 📝 Informe HTML
html = f"""
<html><head><meta charset='utf-8'><title>Informe IoT</title></head><body>
<h1>📊 Informe Automático IoT</h1>
<p>📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

<h2>📌 Análisis de Clústeres</h2>
<img src='clusters.png' width='600'><br><br>
{resumen}
<h3>🔍 Leyenda de Patrones:</h3>
<ul>
  <li><span style='color:red'>🟥 Patrón 1</span></li>
  <li><span style='color:blue'>🟦 Patrón 2</span></li>
  <li><span style='color:green'>🟩 Patrón 3</span></li>
</ul>

<ul>{''.join(interpretaciones)}</ul>

<h2>📈 Tendencias</h2>
<img src='tendencia.png' width='600'>
</body></html>
"""

with open('informe.html', 'w') as f:
    f.write(html)

print("✅ Informe generado correctamente")
