# Configuración en Windows

## Variables de entorno
El archivo `src/infrastructure/config.py` carga las variables desde `.env` (si existe) o del entorno. Claves importantes:
- **DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME**: conexión a MySQL. `docker-compose.yml` expone MySQL en 3306 con usuario `user` y contraseña `password`.
- **EXCEL_REQUIRED_SHEETS**: hojas obligatorias al leer Excel (por defecto `ATC,Encuesta salida`).
- **CSV_BASE_DIR**: carpeta donde se guardan los CSV limpios (`datos_analizados/`).
- **APP_TITLE**: título en la UI de Streamlit.
- **SMTP_SERVER/SMTP_PORT/SMTP_USER/SMTP_PASSWORD/EMAIL_FROM**: parámetros SMTP para envío de resultados.

En PowerShell puedes crear `.env` en la raíz con:
```powershell
@"
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=user
DB_PASSWORD=password
DB_NAME=cosmitos_imperiales_db
CSV_BASE_DIR=datos_analizados
SMTP_SERVER=localhost
SMTP_PORT=1025
EMAIL_FROM=noreply@cosmitos.com
"@ | Set-Content .env
```

## Entorno local
1. Instala Python 3.8+ y ejecuta:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e .
   ```
2. Levanta MySQL con Docker Desktop:
   ```powershell
   docker-compose up -d
   ```
   El script `database_setup.sql` inicializa la base y credenciales.
3. Ejecuta la app:
   ```powershell
   streamlit run src/app.py
   ```
   Abre `http://localhost:8501`.

## Conectividad y permisos
- Asegura que el puerto 3306 esté libre; si usas WSL, exponlo hacia Windows o ajusta `DB_PORT`.
- Las carpetas `datos_analizados/` y `reports/` se crean automáticamente; verifica permisos de escritura en la ruta del proyecto.
- El modelo ML (`src/infrastructure/ML/clasificador_sentimiento_final.pkl`) se carga desde ruta relativa; no mover sin actualizar el contenedor de dependencias.

## SMTP de prueba
Para pruebas locales puedes usar el servidor SMTP falso incluido:
```bash
python mock_smtp_server.py
```
Luego configura `SMTP_SERVER=localhost` y `SMTP_PORT=1025` para enviar correos de prueba desde la UI.
