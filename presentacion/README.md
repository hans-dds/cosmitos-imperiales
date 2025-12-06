# Instrucciones para agregar slides
- En la carpeta slides/ agreguen su parte de la presentación en un archivo Markdown, siguiendo los ejemplos como 00-title.md.

- Para mostrar sus diapositivas, deben agregar su archivo en index.html de la siguiente manera:
```
<section
    data-markdown="slides/00-title.md" <!-- Nombre de su archivo -->
    data-separator="---"
></section>
```

## Ejecución
Necesitan [node.js](https://nodejs.org/es) instalado.

Instalar las dependencias:
```
npm install
```

Ejecutar el proyecto:
```
npm run start
```
La presentación se despliega en `http://localhost:8000`.
