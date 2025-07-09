# 📊 Gráfico de Clústeres
plt.figure()

colores_patron = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Azul, Naranja, Verde

for c in range(3):
    grupo = df[df['cluster'] == c]
    plt.scatter(grupo['temperatura'], grupo['iluminacion'], label=f'Patrón {c+1}', color=colores_patron[c])

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
    interp = f"<li><span style='color:{color}'>🔹 <b>Patrón {idx+1}</b>: Temperatura ~{temp:.1f}°C, Iluminación ~{ilum:.0f} lux.</span> "

    if temp > 29 and ilum > 400:
        interp += "⚠️ Riesgo de sobrecalentamiento por exposición intensa."
    elif temp < 24 and ilum < 200:
        interp += "🌙 Ambientes fríos y oscuros, típicos de la noche."
    elif 25 <= temp <= 28 and 200 <= ilum <= 350:
        interp += "✅ Condiciones ideales de confort térmico."
    else:
        interp += "ℹ️ Combinación atípica, requiere seguimiento."

    interpretaciones.append(interp + "</li>")
