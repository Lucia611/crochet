# 🧶 Mi colección de patrones de crochet

Repositorio personal para guardar patrones de ganchillo, agrupados por temática.

## Organización

```
crochet/
├── README.md              ← este índice
├── glosario.md            ← abreviaturas, equivalencias US/UK/ES, puntos especiales
├── _plantilla.md          ← plantilla para añadir un patrón nuevo
└── navidad/               ← una carpeta por temática
    ├── README.md          ← índice de la temática
    ├── motivos/           ← piezas sueltas reutilizables (hojas, flores, bayas...)
    ├── adornos/           ← proyectos pequeños terminados (árbol, regalos...)
    └── corona-de-puerta/  ← proyecto grande que combina motivos
```

**Criterio:** `temática / tipo de pieza / patrón.md`.
Los *motivos* son piezas pequeñas que se pueden usar solas o combinadas en proyectos más grandes
(por ejemplo, la poinsettia sirve de broche, de adorno de árbol o de pieza de la corona).

## Temáticas

| Temática | Patrones |
|---|---|
| [🎄 Navidad](navidad/README.md) | 9 patrones |

## Cómo añadir un patrón nuevo

1. Copia `_plantilla.md` a la carpeta de la temática (créala si no existe, en minúsculas y sin tildes).
2. Rellénalo y añade una línea al `README.md` de esa temática.
3. Si un patrón usa un punto nuevo, descríbelo en `glosario.md`.

> Si quieres guardar fotos de referencia, crea una carpeta `fotos/` dentro de la temática y enlázalas desde el patrón.

## Web para el móvil

`index.html` es una web estática (sin dependencias salvo `marked` desde cdnjs) con todos los patrones y fotos, pensada para abrir en el móvil o la tablet. Se puede instalar en la pantalla de inicio.

- **Regenerarla** tras cambiar un patrón: `python3 build_site.py` (lee los `.md`, las fotos de `navidad/fotos/` y `sitio/plantilla.html`).
- **Desplegar:** Vercel (o GitHub Pages) sirviendo la raíz del repositorio, sin comando de build.
