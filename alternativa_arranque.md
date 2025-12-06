```
# Arranque completo del proyecto con uv

# 1. Instalar Python 3.11 y fijar la versión para el proyecto
uv python install 3.11
uv python pin 3.11

# 2. Crear y activar el entorno virtual
uv venv
# Linux/MacOS
source .venv/bin/activate
# Windows PowerShell (descomentar si corresponde)
# .\.venv\Scripts\Activate.ps1

# 3. Instalar todas las dependencias del proyecto
uv sync

# 4. Ejecutar la aplicación Streamlit
uv run streamlit run src/app.py
```

5. Estándar de codificación
```
uv tool run flake8 src
```

```
uv tool run ruff check src/ --fix
```