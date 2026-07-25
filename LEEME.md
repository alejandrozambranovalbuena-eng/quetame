# Sistema Inteligente de Alerta Temprana — Quetame (dashboard interactivo) · v8.0

App en Python (Streamlit + Plotly). Autores: Alejandro Zambrano Valbuena, Camilo Torres Hernández,
Leticia Floralba González, Javier Alejandro Flórez.

## Pestañas

1. **Resumen** — problema real (Naranjal, El Algodonal, evento del 17-18 de julio de 2023), objetivo y fuentes.
2. **Monitoreo en vivo** — sensores por zona (batería/señal), gráficos de precipitación/humedad/nivel de río, gauge de riesgo, mapa, payload JSON.
3. **Simulacro** — módulo completo con sliders de escenario, datos históricos de calibración, animación en vivo (gauge + monitor + río en 3D + chat comunitario + registro del sistema) y resumen de reacción de cada actor.
4. **Arquitectura** — 6 capas del sistema + diagrama de flujo (Sankey) + especificaciones técnicas + protocolos.
5. **Actores** — matriz de cuatro hélices con funciones detalladas.
6. **Riesgos & cronograma** — mitigación de riesgos + Gantt interactivo de 18 actividades reales (24 meses).
7. **Impacto** — indicadores estilo Power BI (deltas + gráfico comparativo), antes/después, simulador de cobertura, costos en COP.

## Archivos de esta carpeta

- `app.py` — la aplicación.
- `requirements.txt` — dependencias (streamlit, pandas, numpy, plotly).
- `.streamlit/config.toml` — fuerza el tema claro (importante, sin este archivo el texto puede verse mal en modo oscuro).
- `LEEME.md` — este archivo.

## Correr localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en `http://localhost:8501`.

---

## Publicar el proyecto (tienes GitHub — sigue estos pasos)

### Paso 1 — Crear el repositorio en GitHub

1. Entra a [github.com](https://github.com) e inicia sesión.
2. Arriba a la derecha, clic en el ícono **+** → **New repository**.
3. En "Repository name" escribe, por ejemplo, `quetame-alerta-temprana`.
4. Marca **Public** (así el link de la app funciona sin restricciones en el plan gratis de Streamlit).
5. No marques ninguna casilla adicional.
6. Clic en **Create repository**.

### Paso 2 — Subir los archivos (sin usar comandos, solo el navegador)

1. En la página del repositorio recién creado, busca el enlace que dice **"uploading an existing file"** (o el botón **Add file → Upload files**).
2. Arrastra ahí `app.py`, `requirements.txt` y `LEEME.md`.
3. Clic en **Commit changes** (botón verde abajo).
4. Ahora falta la carpeta oculta `.streamlit/config.toml` — GitHub no siempre deja arrastrar carpetas ocultas, así que créala manualmente:
   - Clic en **Add file → Create new file**.
   - En el campo del nombre escribe exactamente: `.streamlit/config.toml` (con la barra — GitHub crea la carpeta sola).
   - Pega este contenido:
     ```toml
     [theme]
     base = "light"
     primaryColor = "#FF441F"
     backgroundColor = "#FFFFFF"
     secondaryBackgroundColor = "#F5F6F9"
     textColor = "#16181D"
     font = "sans serif"

     [browser]
     gatherUsageStats = false
     ```
   - Clic en **Commit changes**.

### Paso 3 — Desplegar en Streamlit Community Cloud (gratis)

1. Ve a [share.streamlit.io](https://share.streamlit.io).
2. Inicia sesión con **Continue with GitHub** (la misma cuenta del Paso 1).
3. Clic en **New app** (o **Create app**).
4. Selecciona: tu repositorio `quetame-alerta-temprana`, rama `main`, archivo principal `app.py`.
5. Clic en **Deploy**.
6. Espera 1-2 minutos. Te da un link público, algo como `https://quetame-alerta-temprana.streamlit.app`.

Ese link lo puedes compartir directamente con el docente — no necesita instalar nada, se abre en cualquier navegador.

### Para actualizar la app después de publicada

Cualquier cambio futuro: edita el archivo directamente en GitHub (ícono de lápiz) o vuelve a subirlo con **Upload files**. Streamlit Cloud detecta el cambio y actualiza la app sola en un par de minutos.

## Nota importante

La pestaña "Monitoreo en vivo" y el módulo "Simulacro" usan datos simulados para ilustrar cómo operaría el sistema una vez instalados los sensores reales — esto se indica explícitamente dentro de la app.
