# Revisión de Arquitectura Limpia y SOLID

## Resumen
- Capas bien definidas: `src/domain`, `src/use_cases`, `src/adapters`, `src/infrastructure`, `src/app.py`.
- Punto de entrada (`src/app.py`) orquesta página y DI sin lógica de negocio.
- Casos de uso dependen de puertos e inyección — correcto.
- Hallazgo clave: un adaptador (`analysis_repository_adapter.py`) importa utilidades de `use_cases` (mapper de sentimiento), rompiendo dirección de dependencias.
- Repositorio mezcla responsabilidades (SQL, CSV, creación de tabla, transformación) — mejorar SRP/ISP.

## Reglas de Arquitectura Limpia
- Dominio no debe importar `use_cases`/`adapters`/`infrastructure`.
- Use cases solo importan puertos y servicios del dominio.
- Adaptadores implementan puertos y dependen de librerías externas, nunca de `use_cases`.
- Infraestructura compone todo via DI; UI/controladores consumen use cases.

## Sugerencias Prioritarias
1. Mapper de sentimiento
   - Mover `convert_dataframe_classifications` a `src/domain/services/sentiment_mapper.py`.
   - Usarlo desde casos de uso o controlador; eliminar su uso dentro del repositorio.

2. Rediseño de `IAnalysisRepository` (ISP/DIP)
   - Cambiar a interfaz agnóstica del medio de almacenamiento:
     - `save(data, id) -> (bool, str)`
     - `list() -> List[str]`
     - `load(id) -> DataFrame`
     - `delete(id) -> (bool, str)`
     - `delete_many(ids) -> (bool, List[...])`
   - Mantener un adaptador “compuesto” que escribe a MySQL y CSV internamente.

3. Separación de responsabilidades (SRP)
   - Extraer creación de tablas a migraciones (`database_setup.sql`/Alembic) o método privado separado.
   - El repositorio se centra en persistir/leer; sin transformar negocio.
   - Centralizar validación de nombres de tabla; devolver `(False, mensaje)` consistente sin lanzar excepciones.

4. Dirección de dependencias (DIP)
   - Eliminar dependencias de adaptadores hacia `use_cases`.
   - Confirmar que `domain` solo tiene entidades/VO/servicios puros.
   - Asegurar que `use_cases` no consumen utilidades de UI/infrastructure.

5. Controladores/Presentación
   - `StreamlitController`: validar entrada, invocar use cases, mapear a modelos de presentación; evitar reglas de negocio.
   - Componentes de UI solo renderizan y formatean.

6. Nombres/Convenciones de datos
   - Normalizar columnas (`Clasificacion`, `Fiabilidad`, `fecha`) fuera del repositorio.
   - Estándar de `id`/`table_name` manejado por adaptador.

7. Contratos y errores (LSP)
   - Alinear todas las implementaciones al contrato de puertos: tipos de retorno y mensajes coherentes.
   - Evitar excepciones no controladas; capturar y convertir a resultado.

8. Interfaz segregada (ISP)
   - Si alguna implementación no soporta SQL/CSV simultáneos: separar `CsvStore` y `SqlStore` y componer en DI.

## Cambios de bajo riesgo recomendados
- Mover mapper de sentimiento al dominio y actualizar importaciones.
- Quitar la transformación de `load_analysis` del repositorio; aplicar en `load_analysis_use_case` o controlador.
- Adaptar `IAnalysisRepository` a métodos agnósticos y crear un adaptador que delegue a SQL+CSV.
- Encapsular creación de tabla; documentar que las migraciones son la fuente de la verdad del esquema.

## Buenas prácticas adicionales
- Documentar un diagrama de dependencias en `architecture_overview.md` (quién puede importar a quién).
- Añadir tests por capa (cuando decidas ejecutarlos):
  - Use cases con mocks de puertos (orquestación y reglas).
  - Adaptadores con `mysql.connector` mockeado (interacción externa).
  - Servicios de dominio puros (sin dependencias).

## Checklist de verificación rápida
- [ ] Ningún import de `use_cases` en `adapters`.
- [ ] `domain` sin dependencias externas a la app.
- [ ] `use_cases` solo usan `ports` y servicios de dominio.
- [ ] Repositorio sin transformaciones de negocio.
- [ ] DI container es el único ensamblador de implementaciones.
- [ ] Errores convertidos a `(bool, str)` en puertos.

## Plan sugerido de implementación
1) Crear `src/domain/services/sentiment_mapper.py` y mover funciones. (COMPLETADO)
2) Actualizar `load_analysis_use_case`/controlador para aplicar mapeo. (COMPLETADO)
3) Simplificar `IAnalysisRepository` y ajustar `ProcessFileUseCase` a `save(...)`. (COMPLETADO)
4) Encapsular creación de tabla con método privado `_ensure_table_exists`. (COMPLETADO)
5) Revisar UI/controladores para mantenerlos libres de negocio. (PENDIENTE DE VERIFICACIÓN MANUAL)

## Estado de implementación
- Mapper movido al dominio y eliminado uso desde el adaptador.
- Repositorio ahora expone métodos genéricos: `save`, `list`, `load`, `delete`, `delete_many`.
- Casos de uso actualizados para nueva interfaz.
- Creación de tabla encapsulada en `_ensure_table_exists`.
- Transformación de clasificaciones y columna `Fiabilidad` aplicada en caso de uso de carga.

## Notas
- Mantén los cambios mínimos y dirigidos, sin romper la API pública.
- Usa DI para probar nuevas combinaciones de adaptadores sin tocar los casos de uso.
