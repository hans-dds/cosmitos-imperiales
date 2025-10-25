# Configurar y arrancar el proyecto

## Configuración
Iniciar un nuevo entorno.
```
python3 -m venv .venv
```

Activar el entorno (Windows)
```
.\.venv\Scripts\Activate.ps1
```

Activar el entorno (Linux/MacOS)
```
source .venv/bin/activate
```

Instalar dependencias y configurar los módulos
```
pip install -e .
```

## Ejecución
```
streamlit run src/main/app.py
```

También funciona:
```
python3 -m streamlit run src/main/app.py
```