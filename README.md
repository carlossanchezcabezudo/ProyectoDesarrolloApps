# 🚦 MADly Safe · Recomendador de franjas más seguras según perfil y contexto en Madrid

> Visualización sencilla + modelo de ML en Python para estimar **riesgo de lesión grave** condicionado a un escenario elegido por la persona usuaria, y recomendar **franjas horarias alternativas** más seguras dentro del mismo distrito y con el mismo perfil.

---

## 🧩 Breve descripción del problema
Los informes de siniestralidad urbana suelen estar agregados por año o distrito y, aunque útiles para la planificación, resultan poco operativos para decisiones cotidianas como “¿a qué hora me conviene desplazarme con mi perfil y en mi zona?”. **MADly Safe** convierte los datos abiertos de accidentes de la ciudad de Madrid en una **experiencia de una sola pantalla**: la persona define un “personaje” (tipo de persona y de vehículo si procede, rango de edad, sexo, distrito, día, hora y meteorología prevista) y la app devuelve **un porcentaje de severidad** (grave/fallecido vs. no grave) junto a **3–5 franjas horarias cercanas** con menor probabilidad estimada manteniendo fijo el resto del escenario. No pretende predecir si ocurrirá un accidente, sino **la severidad condicionada** a que ocurra; esto permite ofrecer recomendaciones prácticas, auditables y fáciles de comprender.

---

## 🎯 Objetivos principales
- **Modelo de clasificación binaria y validación temporal.** Entrenar un clasificador (baseline de **Regresión Logística** y, si aporta, un **árbol en ensamblado** como Random Forest o Gradient Boosting) para estimar \(p(\text{grave/fallecido} \mid \text{contexto})\), con partición por años para evitar fuga temporal y métricas centradas en **F1 macro** y **ROC-AUC**.
- **Pipeline reproducible en Python.** Implementar un flujo claro de **ingesta → limpieza → codificación → entrenamiento → evaluación → serialización**, usando `pandas` y `scikit-learn`, con semilla fija y scripts independientes para ejecutar de punta a punta.
- **Tratamiento de desbalance y calibración.** Abordar la rareza de los casos graves con `class_weight='balanced'` (o estrategia equivalente) y aplicar **calibración probabilística** cuando sea necesario para que el porcentaje mostrado sea interpretable.
- **Interpretabilidad práctica.** Exponer **coeficientes** (en el caso de logística) y **Permutation Importance** o importancias de los árboles para explicar qué variables impactan más, además de **mensajes en lenguaje natural** que traduzcan el porqué de cada recomendación de franja.
- **Visualización única y clara con Streamlit.** Desarrollar una pantalla con un **formulario de escenario** a la izquierda y, a la derecha, una **tarjeta de riesgo**, un **mini-gráfico de barras** comparando franjas horarias alternativas y una **explicación breve** del resultado.
- **Calidad y trazabilidad.** Documentar decisiones, registrar experimentos básicos (parámetros y métricas), incluir tests ligeros de integridad de datos y asegurar que el repositorio pueda ejecutarse tanto **en local** como **en Google Colab**.
- **Comunicación responsable.** Señalar explícitamente que el modelo **no calcula probabilidad de accidente** sino severidad condicionada; evitar inferencias erróneas y promover un uso informativo y educativo.

---

## 🗓️ Plan inicial de trabajo (Octubre–Diciembre 2025)
**Octubre — Datos, baseline y validación.** Preparar el repositorio y el entorno; descargar y unificar los ficheros del portal (2019–2025) con tipado consistente; normalizar categorías y construir variables de calendario (día de la semana, fin de semana, festivos) y de tiempo (franja horaria); definir la **variable objetivo** (grave/fallecido vs. no grave) y resolver nulos; implementar un **split temporal** (train 2019–2023, validación 2024, test 2025 YTD); entrenar la **regresión logística baseline** con `class_weight='balanced'`, obtener métricas iniciales y registrar resultados, dejando un primer **pipeline reproducible**.

**Octubre/Noviembre — Ingeniería de variables, mejoras y comenzar la visualización.** Incorporar codificaciones categóricas adecuadas (one-hot/target según modelo), refinar variables contextuales (meteorología codificada, interacciones suaves hora×día), explorar un **modelo de árboles** si mejora al baseline, aplicar **calibración** si procede y fijar **umbral operativo**; Implementar la app en **Streamlit** con el **formulario de escenario** y el **panel de resultados** (tarjeta de riesgo, gráfico de comparación horaria y explicación en texto), integrar el modelo serializado y la lógica de recomendación, revisar tiempos de respuesta y mensajes.

**Noviembre/Diciembre — Visualización, integración y entrega.**  Desplegar un **servicio en la nube** que sea accesible mediante una URL pública, probando que todod lo relacionado con la visualización funciona como debería. Redacción de la documentación y de un **README detallado**, ejemplos de uso y preparar la **presentación final** y **demostración** de la aplicación 

---

<p align="center">
  <sub>Python · pandas · scikit-learn · Streamlit</sub>
</p>
