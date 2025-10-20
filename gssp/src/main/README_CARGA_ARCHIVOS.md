# Interfaz de Carga de Archivos

Esta implementación proporciona una interfaz gráfica para la carga de archivos Excel usando PyQt5, siguiendo el patrón de arquitectura MVC (Modelo-Vista-Controlador).

## Estructura del Código

### Vista (`VistaCargaArchivo.py`)
- **Responsabilidad**: Maneja toda la presentación visual y la interacción con el usuario
- **Características**:
  - Ventana principal que simula el wireframe proporcionado
  - Botón "Subir" para iniciar la selección de archivos
  - Etiqueta de estado que muestra el archivo seleccionado
  - Mensajes informativos y de error
  - Señales PyQt5 para comunicación con el controlador

### Controlador (`ControladorCargaArchivo.py`)
- **Responsabilidad**: Gestiona la lógica de negocio para la carga de archivos
- **Características**:
  - Manejo del explorador de archivos nativo del sistema
  - Validación de archivos (existencia, tipo, extensión)
  - Filtrado automático para archivos Excel (.xlsx, .xls)
  - Gestión de errores y comunicación con la vista
  - Estado del archivo seleccionado

## Funcionalidades Implementadas

### ✅ Características Principales

1. **Interfaz Gráfica Intuitiva**
   - Diseño basado en el wireframe proporcionado
   - Título de ventana "Programa.exe"
   - Mensaje instructivo claro
   - Botón de subida prominente

2. **Explorador de Archivos**
   - Diálogo nativo del sistema operativo
   - Filtros automáticos para archivos Excel
   - Soporte para formatos .xlsx y .xls

3. **Validación de Archivos**
   - Verificación de existencia del archivo
   - Validación de extensión
   - Verificación de que es un archivo válido

4. **Retroalimentación al Usuario**
   - Estado visual del archivo seleccionado
   - Mensajes de confirmación
   - Manejo de errores con mensajes descriptivos

5. **Arquitectura Limpia**
   - Separación clara entre vista y controlador
   - Comunicación mediante señales PyQt5
   - Bajo acoplamiento entre componentes

## Instalación de Dependencias

```bash
# Instalar PyQt5
pip install PyQt5
```

## Uso

### Ejecución Básica

```python
# Desde el directorio principal
cd gssp/src/main
python ejemplo_carga_archivo.py
```

### Uso Programático

```python
from presentacion.Controlodores.ControladorCargaArchivo import ControladorCargaArchivo
from PyQt5.QtWidgets import QApplication

# Crear aplicación
app = QApplication([])

# Inicializar controlador
controlador = ControladorCargaArchivo()
controlador.inicializar()

# Mostrar interfaz
controlador.mostrar_vista()

# Ejecutar aplicación
app.exec_()

# Verificar archivo seleccionado
if controlador.hay_archivo_seleccionado():
    print(f"Archivo: {controlador.obtener_nombre_archivo()}")
    print(f"Ruta: {controlador.obtener_ruta_archivo()}")
```

## API del Controlador

### Métodos Principales

- `inicializar()`: Inicializa la vista y conecta eventos
- `mostrar_vista()`: Muestra la ventana principal
- `obtener_ruta_archivo()`: Retorna la ruta completa del archivo seleccionado
- `obtener_nombre_archivo()`: Retorna el nombre del archivo seleccionado
- `hay_archivo_seleccionado()`: Verifica si hay un archivo seleccionado
- `limpiar_seleccion()`: Limpia la selección actual

### Eventos y Señales

- La vista emite la señal `archivo_seleccionado` cuando se hace clic en "Subir"
- El controlador maneja automáticamente la apertura del explorador
- La validación y retroalimentación son automáticas

## Flujo de Trabajo

1. **Usuario hace clic en "Subir"**
   - La vista emite señal `archivo_seleccionado`
   - El controlador recibe la señal

2. **Apertura del Explorador**
   - Se abre el diálogo nativo del sistema
   - Filtros automáticos para archivos Excel

3. **Selección del Archivo**
   - Usuario selecciona archivo o cancela
   - Validación automática si se selecciona

4. **Actualización de la Interfaz**
   - Estado del archivo se actualiza visualmente
   - Mensajes de confirmación o error

## Extensibilidad

### Para Agregar Nuevas Validaciones

```python
# En el controlador, método procesar_archivo_seleccionado
def procesar_archivo_seleccionado(self, ruta_archivo: str):
    # ... validaciones existentes ...
    
    # Agregar nueva validación
    if not self.validar_estructura_excel(ruta_archivo):
        self.vista.mostrar_error("El archivo no tiene la estructura requerida.")
        return
```

### Para Conectar con Otras Capas

```python
# El controlador puede ser extendido para interactuar con servicios
def procesar_archivo_seleccionado(self, ruta_archivo: str):
    # ... validaciones ...
    
    # Integrar con capa de negocio (futuro)
    # from negocio.ServicioValidarArchivo import ServicioValidarArchivo
    # servicio = ServicioValidarArchivo()
    # if servicio.validar_formato_archivo(ruta_archivo):
    #     # Proceder con el análisis
```

## Notas de Implementación

- **Patrón de Señales**: Se usa el sistema de señales de PyQt5 para comunicación asíncrona
- **Manejo de Errores**: Todos los errores se capturan y se muestran al usuario
- **Filtros de Archivo**: Solo se pueden seleccionar archivos Excel
- **Validación Robusta**: Se verifican múltiples aspectos del archivo antes de aceptarlo
- **Interfaz Responsiva**: La UI se actualiza inmediatamente tras las acciones del usuario

Esta implementación proporciona una base sólida para la funcionalidad de carga de archivos y puede ser fácilmente extendida para integrarse con las capas de negocio y datos del sistema.
