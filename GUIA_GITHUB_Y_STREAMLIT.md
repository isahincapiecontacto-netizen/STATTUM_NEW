# Publicar la nueva versión de STATTUM

## 1. Crear el repositorio nuevo

1. Entra a https://github.com/new e inicia sesión.
2. En **Repository name** escribe, por ejemplo, `STATTUM-Concurso`.
3. Selecciona **Public** si deseas alojar el código en Streamlit Community Cloud.
4. Puedes dejar sin marcar las opciones de inicialización (README, .gitignore), pues ya se incluyen aquí.
5. Pulsa **Create repository**.

## 2. Subir los archivos

1. Descomprime el archivo ZIP recibido.
2. Abre el repositorio recién creado en GitHub.
3. Elige **Add file → Upload files**.
4. Sube **el contenido de la carpeta** `STATTUM_Concurso`, no el ZIP ni una carpeta extra que envuelva `app.py`.
5. Asegúrate de que en la raíz aparezcan `app.py`, `requirements.txt`, `config.py` y los demás archivos, y que también se hayan subido las carpetas `assets/` y `.streamlit/`.
6. Escribe un mensaje como `Primera versión STATTUM Concurso` y pulsa **Commit changes**.

**Importante para la publicación:** el nombre de la carpeta `assets` y de la carpeta `.streamlit` debe conservarse exactamente; asegúrate de que `.streamlit/config.toml` se incluya (es una carpeta oculta).

### Si GitHub no acepta subir la carpeta `.streamlit`

Utiliza `Add file → Create new file` y escribe el nombre `.streamlit/config.toml`; copia su contenido del ZIP. Los archivos invisibles pueden no aparecer en algunos exploradores de Windows si están ocultos.

## 3. Publicarla en Streamlit Community Cloud

1. Abre https://share.streamlit.io/ y accede con tu cuenta de GitHub.
2. Selecciona **Create app → Deploy a public app from GitHub** (el nombre puede variar).
3. Elige el repositorio nuevo y la rama `main`.
4. En **Main file path** escribe exactamente `app.py`.
5. Escoge un nombre de dirección web disponible y pulsa **Deploy**.
6. Al cargar, verifica las cuatro secciones: **Inicio, Análisis, Simulador y Conclusiones**.

## 4. Qué comprobar antes del concurso

- **Inicio:** se ve el logo original y el botón «Comenzar análisis» abre Análisis.
- **Análisis:** se muestran los colores originales de los cuatro activos, se ven los gráficos y se puede añadir y retirar un ticker válido.
- **Simulador:** el monto, el plazo y el activo elegido producen escenarios Monte Carlo; el botón de la gráfica permite reproducir sus trayectorias.
- **Conclusiones:** los textos cambian con la selección de activos y muestran la última simulación si corresponde.
- **Presentación:** comprueba que el proyecto carga desde una ventana privada y que el internet del lugar funciona.

Los datos dependen de Yahoo Finance; si un símbolo no tiene precios, la aplicación lo informa sin inventar resultados. Si se cae el servicio, conviene tener preparadas capturas de respaldo del proyecto, pero estas **no** sustituyen datos reales en la aplicación.

## 5. Si quieres actualizar el diseño

- Colores originales y fecha base → `config.py`.
- Textos y contenido de las cuatro pestañas → `app.py`.
- Fondos, botones, tarjetas, animación de entrada → `estilos.py`.
- Gráficos y animación Monte Carlo → `figuras.py`.
- Reglas del simulador → `simulacion.py`.
- Cálculos financieros → `metricas.py`.

**El repositorio original no se borra ni modifica.** Esta es una versión nueva e independiente.
