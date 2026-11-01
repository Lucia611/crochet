#!/usr/bin/env python3
"""Genera index.html (web estática del cuaderno) a partir de los .md y las fotos.

Uso:
    python3 build_site.py                 # escribe index.html en la raíz
    python3 build_site.py fragmento.html  # además, escribe un fragmento para publicar como Artifact

Para añadir un patrón: créalo en su carpeta, añade su ficha en THEMES (abajo) y ejecuta el script.
Para añadir una temática: añade otro elemento a THEMES.
"""
import base64, io, json, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
FOTOS = f'{ROOT}/navidad/fotos'

# ---- Documentos (id -> ruta del .md) -------------------------------------------------------
PATTERN_FILES = {
    'hojas-texturizadas': 'navidad/motivos/hojas-texturizadas.md',
    'poinsettia': 'navidad/motivos/poinsettia.md',
    'pina': 'navidad/motivos/pina.md',
    'bayas': 'navidad/motivos/bayas.md',
    'campana': 'navidad/motivos/campana.md',
    'lazo': 'navidad/motivos/lazo.md',
    'mini-corona-bobbles': 'navidad/adornos/mini-corona-bobbles.md',
    'campanas-nordicas': 'navidad/adornos/campanas-nordicas.md',
    'corona-de-puerta': 'navidad/corona-de-puerta/corona-de-puerta.md',
}
GUIDE_FILES = {
    'puntos': 'cuaderno/puntos.md',
    'consejos': 'cuaderno/consejos.md',
    'ganchos-e-hilos': 'cuaderno/ganchos-e-hilos.md',
    'glosario': 'glosario.md',
}

# ---- Fichas de patrones y temáticas ---------------------------------------------------------
# foto: archivo de navidad/fotos usado para la portada y las miniaturas
THEMES = [{
    'id': 'navidad', 'name': 'Navidad', 'foto': 'poinsettia.jpg',
    'tagline': 'Coronas, flores de Pascua, campanas y adornos de árbol.',
    'groups': [
        {'title': 'Motivos', 'note': 'Piezas sueltas que se usan solas o dentro de proyectos más grandes.', 'items': [
            {'id': 'hojas-texturizadas', 'name': 'Hojas texturizadas', 'level': 'Principiante', 'size': '7 × 4 cm', 'desc': 'Hoja en rombo con costillas, en tres verdes.', 'foto': 'hojas.jpg'},
            {'id': 'poinsettia', 'name': 'Poinsettia', 'level': 'Intermedio', 'size': '7 – 15 cm', 'desc': 'Flor 3D en capas, mini de 2 capas y versión por pétalos.', 'foto': 'poinsettia-detalle.jpg'},
            {'id': 'pina', 'name': 'Piña', 'level': 'Intermedio', 'size': '6 × 4,5 cm', 'desc': 'Cuerpo amigurumi con bobbles escalonados como escamas.', 'foto': 'pina.jpg'},
            {'id': 'bayas', 'name': 'Bayas', 'level': 'Principiante', 'size': '2 – 3 cm', 'desc': 'Bolitas rojas y crudas para hacer racimos.', 'foto': 'bayas.jpg'},
            {'id': 'campana', 'name': 'Campana sencilla', 'level': 'Intermedio', 'size': '5 cm', 'desc': 'Con costillas y badajo de cuenta de madera.', 'foto': 'campana.jpg'},
            {'id': 'lazo', 'name': 'Lazo grande', 'level': 'Principiante', 'size': '18 cm', 'desc': 'Lazo verde con dos colas para la parte alta de la corona.', 'foto': 'corona-puerta.jpg'},
        ]},
        {'title': 'Adornos de árbol', 'note': 'Proyectos pequeños y terminados.', 'items': [
            {'id': 'mini-corona-bobbles', 'name': 'Mini corona de bobbles', 'level': 'Intermedio', 'size': '6,5 cm', 'desc': 'Con lazo de cordel y cuentas de madera.', 'foto': 'mini-corona.jpg'},
            {'id': 'campanas-nordicas', 'name': 'Campanas nórdicas', 'level': 'Avanzado', 'size': '10 × 8 cm', 'desc': 'Base con lazo o flor, malla dorada, hojas en cascada y colores joya.', 'foto': 'campanas-nordicas.jpg'},
        ]},
        {'title': 'Proyectos', 'note': 'Combinan varios motivos.', 'items': [
            {'id': 'corona-de-puerta', 'name': 'Corona de puerta', 'level': 'Intermedio', 'size': '35 cm', 'desc': 'Cantidades de cada pieza y orden de montaje.', 'foto': 'corona-puerta.jpg'},
        ]},
    ],
}]
FEATURED = ['corona-de-puerta', 'campanas-nordicas', 'poinsettia', 'mini-corona-bobbles']
MOSAIC = ['campanas-nordicas.jpg', 'poinsettia-detalle.jpg', 'pina.jpg', 'mini-corona.jpg', 'bayas.jpg', 'hojas.jpg']
GUIDES = [
    {'id': 'puntos', 'name': 'Los puntos', 'desc': 'Cómo se hace cada punto, con sus símbolos de esquema, anillo mágico y disminución invisible.', 'syms': [0, 1, 2, 3, 4, 5]},
    {'id': 'consejos', 'name': 'Consejos y trucos', 'desc': 'Tensión, contar puntos, rellenar, rematar, almidonar y qué hacer si algo sale mal.', 'syms': [2, 3, 4]},
    {'id': 'ganchos-e-hilos', 'name': 'Ganchos e hilos', 'desc': 'Tabla de ganchos en mm y letras, equivalencias de hilos y qué se usa en cada patrón.', 'syms': [0, 2]},
    {'id': 'glosario', 'name': 'Glosario', 'desc': 'Abreviaturas, equivalencias US / UK y puntos especiales.', 'syms': [1, 3]},
]


def jpeg_uri(im, quality=76):
    buf = io.BytesIO()
    im.convert('RGB').save(buf, 'JPEG', quality=quality, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def crop(name, w, h):
    im = Image.open(f'{FOTOS}/{name}').convert('RGB')
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return jpeg_uri(im.crop((l, t, l + w, t + h)), 72)


def doc_from(path):
    md = open(f'{ROOT}/{path}', encoding='utf-8').read()
    title = re.search(r'^# (.+)$', md, re.M).group(1)

    def uri(m):
        im = Image.open(f'{FOTOS}/{m.group(2)}').convert('RGB')
        if im.width > 760:
            im = im.resize((760, int(im.height * 760 / im.width)), Image.LANCZOS)
        return m.group(1) + jpeg_uri(im, 80) + ')'

    md = re.sub(r'(!\[[^\]]*\]\()\.\./fotos/([^)]+)\)', uri, md)
    return {'path': path, 'title': title, 'md': md}


docs = {i: doc_from(p) for i, p in {**PATTERN_FILES, **GUIDE_FILES}.items()}
for t in THEMES:
    t['cover'] = crop(t['foto'], 640, 400)
    for g in t['groups']:
        for it in g['items']:
            it['cover'] = crop(it['foto'], 480, 360)
            it['thumb'] = crop(it['foto'], 160, 160)

data = {'themes': THEMES, 'docs': docs, 'guides': GUIDES, 'featured': FEATURED,
        'mosaic': [crop(m, 420, 420) for m in MOSAIC]}
js = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')

body = open(f'{ROOT}/sitio/plantilla.html', encoding='utf-8').read().replace('__DATA__', js)

# index.html: documento completo (Vercel / GitHub Pages / abrir en el navegador)
i = body.index('</style>') + len('</style>')
head, rest = body[:i].replace('<meta name="claude:viewport-fit-sides" content="cover">', ''), body[i:]
page = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="theme-color" content="#1f4d3b">\n'
        '<link rel="manifest" href="manifest.webmanifest">\n'
        '<link rel="icon" href="icon-192.png">\n'
        '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
        + head + '\n<style>body{margin:0}</style>\n</head>\n<body>\n' + rest + '\n</body>\n</html>\n')
open(f'{ROOT}/index.html', 'w', encoding='utf-8').write(page)
print('index.html', len(page), 'bytes')

if len(sys.argv) > 1:
    open(sys.argv[1], 'w', encoding='utf-8').write(body)
    print(sys.argv[1], len(body), 'bytes')
