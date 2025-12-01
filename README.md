# Gestor de Satisfacción y Seguimiento de Posventa (GSSP)

## Requisitos Previos

- Python 3.8 o superior
- Docker y Docker Compose
- pip

## Configuración

### 1. Crear entorno virtual

```bash
python3 -m venv .venv
```

### 2. Activar entorno virtual

**Windows (PowerShell):**
```bash
.\.venv\Scripts\Activate.ps1
```

**Linux/MacOS:**
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -e .
```

### 4. Configurar base de datos con Docker Compose

Iniciar el contenedor de MySQL:

```bash
docker-compose up -d
```

Esto iniciará MySQL en el puerto 3306 con la siguiente configuración:
- **Base de datos:** `cosmitos_imperiales_db`
- **Usuario:** `user`
- **Contraseña:** `password`
- **Root password:** `rootpassword`

El script `database_setup.sql` se ejecutará automáticamente al iniciar el contenedor.

### 5. Configurar variables de entorno (opcional)

Crear un archivo `.env` en la raíz del proyecto si deseas cambiar la configuración por defecto:

```env
DB_HOST=localhost
DB_USER=user
DB_PASSWORD=password
DB_NAME=cosmitos_imperiales_db
```

## Ejecución

```bash
streamlit run src/app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## Detener la base de datos

Para detener el contenedor de MySQL:

```bash
docker-compose down
```

Para detener y eliminar los volúmenes (esto eliminará los datos):

```bash
docker-compose down -v
```
