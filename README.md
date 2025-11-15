# 🚦 MADly Safe  
### Recomendador de franjas más seguras según perfil y contexto en Madrid

---

Hay preguntas que los informes oficiales de siniestralidad no responden del todo:

> “Si mañana voy en coche al centro, con mi edad y a esa hora…  
> ¿es buena idea, o habría una franja un poco más segura?”

Los datos existen. El Ayuntamiento de Madrid publica años y años de accidentes con víctimas, pero casi siempre se presentan en tablas agregadas, gráficas por distrito o mapas estáticos. Útiles para planificar, sí… pero poco prácticos para decidir **cuándo** moverse en el día a día.

**MADly Safe** nace precisamente de ahí:  
de la idea de **traducir esos datos en una herramienta que hable el idioma de una persona normal**, no solo de una estadística.

---

## 🧠 ¿Qué hace exactamente MADly Safe?

MADly Safe es una aplicación web construida con **Python + Dash** que:

1. Deja que la persona usuaria defina un **escenario de desplazamiento**:
   - tipo de persona (conductor, pasajero, peatón),
   - tipo de vehículo,
   - rango de edad,
   - sexo,
   - distrito de Madrid,
   - día de la semana,
   - franja horaria,
   - estado meteorológico.

2. Con esa información, un **modelo de Machine Learning** entrenado con datos históricos estima:

   > la probabilidad de que, **si ocurre un accidente**, la lesión sea **grave o mortal**.

   No predice si vas a tener un accidente, sino **qué severidad tendría si lo hubiera**.

3. A partir de ahí, el modelo prueba el mismo escenario en **otras franjas horarias posibles** y propone hasta **tres alternativas** dentro del mismo distrito y contexto, del tipo:

   - `18:00–21:59 (Opción A)`,
   - `14:00–17:59 (Opción B)`,
   - `06:00–09:59 (Opción C)`.

   Cada una viene con su probabilidad estimada y se compara visualmente en un gráfico de barras.

El resultado es una experiencia de una sola pantalla:  
un **formulario** a la izquierda y un **panel de riesgo + franjas alternativas** a la derecha.

---

## 🧩 De dónde salen los datos

> ⚠️ Por tamaño/licencia, el Excel original no se versiona completo en GitHub.  
> Se puede obtener desde el **Portal de Datos Abiertos del Ayuntamiento de Madrid**  
> (Accidentes de tráfico con víctimas, años recientes: 2019–2025).

A partir de esos ficheros, el pipeline de datos hace:

- **Unificación de años**: lectura de varios ficheros anuales y concatenación.
- **Limpieza básica**:
  - tipado de fechas y horas,
  - normalización de textos (acentos, mayúsculas, categorías).
- **Construcción de variables de contexto**:
  - `dia_semana` (Lunes–Domingo),
  - `franja_horaria` (00–05:59, 06–09:59, …),
  - variables derivadas en los notebooks (p.ej. “fin de semana”, “noche”, etc.).
- **Homogeneización de categorías**:
  - `tipo_persona` (Conductor, Pasajero, Peatón),
  - `tipo_vehiculo` (Turismo, Moto, VMP, etc.),
  - `rango_edad`,
  - `sexo`,
  - `distrito`,
  - `estado_meteorológico`.

Todo este flujo está encapsulado en `src/etl.py` y documentado paso a paso en los notebooks de la carpeta `notebooks/`.

---

## 🎯 Qué intenta predecir el modelo

La variable objetivo se define como:

- **1 (grave)** → accidentes en los que la víctima sufre **lesión grave o fallece**,  
- **0 (no grave)** → accidentes con víctimas con lesiones leves.

El modelo estima:

\[
P(\text{lesión grave o fallecimiento} \mid \text{contexto})
\]

donde el contexto incluye:

- tipo de persona,
- tipo de vehículo,
- rango de edad, sexo,
- distrito,
- día de la semana,
- franja horaria,
- estado meteorológico.

📌 **Muy importante**:  
Es una probabilidad **condicionada a que ocurra un accidente**. La app nunca dice “tienes un X% de tener un accidente”, sino:

> “Si se produjera un accidente en este escenario, el riesgo de que fuera grave es aproximadamente X%”.

---

## 🤖 Modelos de Machine Learning probados

El modelado se realiza con **scikit-learn**, y está documentado en los notebooks (por ejemplo `02_modelo_baseline.ipynb` y `03_modelos_avanzados.ipynb`).

### 1. Preparación de los datos para ML

- División temporal para evitar fuga de información:
  - **Train**: años más antiguos (p.ej. 2019–2022),
  - **Validación**: año intermedio (p.ej. 2023),
  - **Test**: año más reciente disponible (2024/2025).
- Todas las variables de entrada son categóricas:
  - se usan `OneHotEncoder` + `ColumnTransformer`,
  - se imputan nulos con la categoría más frecuente.

### 2. Modelos explorados

- **Regresión Logística**:
  - `class_weight="balanced"` para compensar la minoría de casos graves.
  - Es el modelo baseline y el más interpretable.
- **Random Forest**:
  - mejor capacidad para capturar interacciones no lineales,
  - evaluado con pesos de clase balanceados.
- **Otros ensambles**:
  - HistGradientBoosting, según versión de librerías.

Se comparan métricas como:

- **ROC-AUC** en validación y test,
- **F1-macro**, más sensible a desequilibrios,
- matriz de confusión para entender errores (falsos positivos/negativos),
- curvas ROC y Precision–Recall.

*(Aquí puedes rellenar los números concretos si ya los tienes medidos, algo así:  
“En test, la Regresión Logística obtiene ROC-AUC ≈ 0.xx y F1-macro ≈ 0.xx, mientras que el Random Forest mejora/empeora en…”)*

### 3. Modelo elegido

El modelo que finalmente se integra en la aplicación es una:

> **Regresión Logística con `class_weight="balanced"`**  
> envuelta en un pipeline con preprocesado (one-hot encoding).

Motivos:

- ofrece un rendimiento competitivo en validación y test,
- es rápido de entrenar y de servir en una API/app,
- es sencillo de explicar (coeficientes y odds ratios),
- se integra de forma limpia en scikit-learn + joblib.

Este pipeline se guarda en:

```text
models/modelo_mejor_2025.joblib
### 3. Modelo elegido

Tras comparar varias familias de modelos, la aplicación se queda con una **Regresión Logística** con `class_weight="balanced"` como corazón de MADly Safe.

No es una elección casual: la regresión logística ofrece un equilibrio interesante entre tres cosas que en este proyecto importan mucho:

- **Rendimiento**: alcanza métricas competitivas en F1-macro y ROC-AUC en los conjuntos de validación y test.
- **Estabilidad**: su comportamiento es menos caprichoso que el de algunos modelos más complejos cuando cambian ligeramente los datos.
- **Interpretabilidad**: sus coeficientes permiten explicar, al menos cualitativamente, qué variables y categorías empujan el riesgo hacia arriba o hacia abajo.

En los notebooks de modelado se exploran alternativas como Random Forest u otros ensambles, pero la decisión final es pragmática:  
para una primera versión de una herramienta educativa y de apoyo a la decisión, **es preferible un modelo algo más simple pero explicable** a uno opaco que sea ligeramente mejor en una métrica pero mucho más difícil de justificar.

La regresión logística se integra en un *pipeline* junto con el preprocesado (imputación + one-hot encoding), de modo que MADly Safe siempre recibe los datos en bruto (las categorías tal y como las selecciona la persona usuaria) y delega en el pipeline toda la transformación necesaria para llegar a la predicción.

---

## 🔍 Cómo decide la app las franjas alternativas

La función que toma las decisiones de fondo se llama `calcular_riesgo` y vive en `src/model.py`. Su misión es doble:

1. Estimar la probabilidad de que, dado un determinado escenario, un accidente sea grave o mortal.
2. Buscar en qué otras franjas horarias, manteniendo el resto del contexto fijo, el modelo estima un riesgo menor.

El proceso, contado en voz humana, sería algo así:

1. **Se limpia lo que viene del formulario**  
   Algunos valores llegan con ligeras variaciones respecto a cómo aparecen en los datos originales (por ejemplo, `"Miercoles"` frente a `"Miércoles"`, o `"Lluvia debil"` frente a `"Lluvia débil"`). Antes de preguntar al modelo, la función normaliza esos textos para que encajen con lo que el pipeline espera.

2. **Se calcula el riesgo para la franja actual**  
   Con el perfil, distrito, día, franja y meteorología proporcionados, se construye un pequeño DataFrame de una fila y se pasa por el pipeline de scikit-learn. De ahí sale `riesgo_principal`, un número entre 0 y 1 que se convierte en porcentaje en la app.

3. **Se exploran todas las franjas posibles**  
   Manteniendo el mismo perfil (tipo de persona, vehículo, edad, sexo), el mismo distrito, el mismo día y la misma meteorología, la función cambia únicamente la franja horaria por cada una de las franjas definidas:
   - madrugada (`00:00–05:59`),
   - mañana punta (`06:00–09:59`),
   - media mañana (`10:00–13:59`),
   - tarde (`14:00–17:59`),
   - tarde punta (`18:00–21:59`),
   - noche (`22:00–23:59`).

   Para cada una de ellas, vuelve a preguntar al modelo y guarda la probabilidad correspondiente.

4. **Se eligen las candidatas más seguras**  
   Una vez calculadas todas las probabilidades, se descarta la franja actual y se ordenan las demás de menor a mayor riesgo. La función prioriza aquellas franjas cuyo riesgo es realmente inferior al de la franja seleccionada, y si no hubiera suficientes, las completa con las siguientes más bajas. Al final se seleccionan hasta **tres** franjas alternativas.

5. **Se generan las etiquetas legibles**  
   Cada alternativa se presenta con una etiqueta tipo:
   - `"18:00–21:59 (Opción A)"`,
   - `"14:00–17:59 (Opción B)"`,
   - `"06:00–09:59 (Opción C)"`.

   De ese modo, la persona usuaria no solo ve que existe una “Opción A” más segura, sino que sabe exactamente **qué franja horaria** representa.

La función devuelve tanto el riesgo de la franja actual como la lista de alternativas, y es la capa de presentación (Dash) la que se encarga de convertir esos números en una experiencia visual y textual.

---

## 🖥️ Interfaz de MADly Safe (Dash)

La interfaz de MADly Safe está construida con **Dash**, una librería de Python que permite crear aplicaciones web interactivas a partir de componentes declarativos.

La estructura de la pantalla es intencionadamente simple:

### 1. Columna izquierda: “Define tu escenario”

En esta zona se agrupan todos los controles del formulario:

- tipo de persona (conductor, pasajero, peatón),
- tipo de vehículo (turismo, motocicleta, VMP, etc.),
- rango de edad,
- sexo,
- distrito de Madrid,
- día de la semana,
- franja horaria,
- estado meteorológico.

La idea es que la persona pueda “montar” un pequeño personaje y una situación concreta en unos pocos clics. Cada cambio en estos selectores dispara el callback principal del modelo.

### 2. Columna derecha: “Riesgo estimado y franjas alternativas”

Aquí se presentan los resultados, siempre en tres capas:

1. **Tarjeta de riesgo**  
   Una tarjeta amarilla recoge el número que suele llamar más la atención:  
   el porcentaje estimado de lesión grave o fallecimiento condicionado a que ocurra un accidente.  
   Debajo se recuerda explícitamente la interpretación condicional y aparece una pequeña nota del tipo:

   > “Modelo actual: Regresión Logística (`class_weight='balanced'`).”

2. **Gráfico de barras comparativo**  
   Un gráfico de barras muestra:
   - en la primera barra, la franja seleccionada,
   - en las siguientes, las franjas alternativas elegidas (Opción A, B y C, con su rango horario explícito).

   Cada barra está etiquetada con su porcentaje, lo que ayuda a ver en qué medida mejora (o no) el riesgo cambiando de franja.

3. **Texto explicativo en lenguaje natural**  
   Bajo el gráfico, un párrafo resume lo que está pasando:  
   menciona el riesgo de la franja actual, enumera las franjas alternativas concretas y recuerda que todo lo demás se mantiene fijo (perfil, distrito, día, meteorología).  
   También aparece un aviso claro de que se trata de una herramienta informativa, basada en datos históricos, y no de una garantía de seguridad.

---

## 🧪 Cómo ejecutar la app en local

La intención es que cualquier persona con conocimientos básicos de Python pueda ejecutar MADly Safe en su propio entorno sin demasiadas complicaciones.

Los pasos típicos son:

1. **Clonar o descargar el repositorio**

   Puedes clonar el proyecto con Git o descargar el ZIP desde GitHub:

   - Clonar:
     
       git clone https://github.com/carlossanchezcabezudo/ProyectoDesarrolloApps.git
       cd ProyectoDesarrolloApps

   - O bien descargar el ZIP y descomprimirlo en una carpeta de tu elección.

2. **Crear y activar un entorno virtual (recomendado)**

   En Windows:

       python -m venv venv
       venv\Scripts\activate

   En Linux/Mac:

       python -m venv venv
       source venv/bin/activate

3. **Instalar las dependencias**

   Desde la raíz del proyecto:

       pip install -r requirements.txt

4. **Asegurarse de que el modelo entrenado está disponible**

   Es necesario haber generado previamente el modelo final desde los notebooks y tener el archivo correspondiente en la carpeta `models/`.  
   Si no existe, se puede volver a ejecutar el notebook de entrenamiento y guardar el pipeline.

5. **Lanzar la aplicación**

   Con el entorno activado, basta con:

       python app.py

   y, a continuación, abrir en el navegador:

       http://127.0.0.1:8050

   Mientras el proceso esté en marcha, la aplicación seguirá atendiendo las peticiones en esa URL.

---

## ☁️ Despliegue en Render (modo resumen)

MADly Safe está pensado para poder desplegarse en Render (u otro proveedor similar) sin necesidad de tocar código.

La lógica de despliegue es la siguiente:

- El archivo `app.py` en la raíz expone un objeto `server` compatible con WSGI, que es lo que espera `gunicorn` (y por extensión, plataformas como Render).
- `requirements.txt` declara las dependencias de Python necesarias para instalar el proyecto.
- Un `Procfile` indica el comando de arranque para el servidor en producción, por ejemplo:

      web: gunicorn app:server

- Un archivo `render.yaml` describe el servicio para que Render pueda configurarlo automáticamente:
  - tipo de servicio (web),
  - lenguaje (Python),
  - plan (gratuito, en este caso),
  - comandos de build y start.

El flujo típico de despliegue sería:

1. Tener el proyecto en un repositorio de GitHub.
2. Crear un nuevo servicio web en Render y vincularlo con ese repositorio.
3. Dejar que Render ejecute `pip install -r requirements.txt` y lance `gunicorn app:server`.
4. Observar el log de construcción y, si todo va bien, obtener una URL pública desde la que acceder a MADly Safe.

Este despliegue pone en práctica el ciclo completo: desde la exploración de datos hasta una **aplicación de análisis de riesgo accesible desde el navegador**.

---

## 📁 Estructura del proyecto

Aunque internamente haya varios scripts y notebooks, la organización general intenta ser clara y sostenible:

- En la raíz del proyecto viven los archivos de “orquestación”:
  - el `app.py` de entrada,
  - el `Procfile`,
  - el `render.yaml`,
  - el `requirements.txt`,
  - y el propio `README.md`.

- La carpeta `src/` contiene el código de la aplicación:
  - `app.py`, con la definición de la interfaz y los callbacks de Dash,
  - `etl.py`, con las funciones de carga y preparación de datos,
  - `model.py`, con la lógica de carga del modelo y cálculo del riesgo y de las franjas alternativas,
  - el fichero `__init__.py` que marca la carpeta como un paquete de Python.

- La carpeta `notebooks/` recoge el trabajo exploratorio y de modelado:
  - notebooks de exploración y limpieza,
  - del modelo baseline,
  - y de comparación de modelos y métricas.

- La carpeta `models/` guarda el modelo entrenado listo para usar en la app.

- La carpeta `data/` (cuando se incluye) aloja los ficheros de datos originales o intermedios, normalmente descargados del portal abierto.

Esta estructura busca que sea fácil entender **qué parte del código corresponde a preparación de datos, cuál al modelo, y cuál a la interfaz de usuario**.

---

## ⚠️ Limitaciones y posibles extensiones

MADly Safe no pretende ser un oráculo, y es importante dejar claras sus limitaciones:

- Solo estima la severidad **condicional** a que ocurra un accidente. No responde a la pregunta “¿tendré un accidente?”, sino “si lo hubiera, ¿con qué probabilidad sería grave o mortal?”.
- Se alimenta de datos históricos que pueden tener sesgos:
  - cambios en la forma de registrar los accidentes,
  - posibles infrarregistros,
  - ausencia de información relevante (tipo de vía, velocidad, densidad de tráfico…).
- La meteorología se incorpora de forma relativamente sencilla; no se integran aún fuentes externas como predicciones en tiempo real.

A cambio, abre muchas puertas para evolucionar el proyecto:

- probar modelos más sofisticados (gradient boosting avanzado, XGBoost, LightGBM) con una calibración de probabilidades más fina,
- incorporar **explicabilidad local** (por ejemplo, con SHAP) que muestre, para un escenario concreto, qué variables empujan la predicción hacia arriba o hacia abajo,
- añadir nuevas variables contextuales:
  - información sobre el tipo de vía,
  - restricciones de tráfico,
  - eventos puntuales que puedan afectar a la movilidad,
- o incluso transformar el recomendador en una API detrás de una app móvil o una integración con otros sistemas.
