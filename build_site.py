import json, re, sys, base64, io
from PIL import Image
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

files = {
    'hojas-texturizadas': 'navidad/motivos/hojas-texturizadas.md',
    'poinsettia': 'navidad/motivos/poinsettia.md',
    'pina': 'navidad/motivos/pina.md',
    'bayas': 'navidad/motivos/bayas.md',
    'campana': 'navidad/motivos/campana.md',
    'lazo': 'navidad/motivos/lazo.md',
    'mini-corona-bobbles': 'navidad/adornos/mini-corona-bobbles.md',
    'campanas-nordicas': 'navidad/adornos/campanas-nordicas.md',
    'corona-de-puerta': 'navidad/corona-de-puerta/corona-de-puerta.md',
    'glosario': 'glosario.md',
}
docs = {}
for id_, path in files.items():
    md = open(f'{ROOT}/{path}', encoding='utf-8').read()
    title = re.search(r'^# (.+)$', md, re.M).group(1)
    def uri(m):
        f = m.group(2)
        im = Image.open(f'{ROOT}/navidad/fotos/{f}').convert('RGB')
        if im.width > 760: im = im.resize((760, int(im.height*760/im.width)), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, 'JPEG', quality=80, optimize=True)
        return m.group(1) + 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode() + ')'
    md = re.sub(r'(!\[[^\]]*\]\()\.\./fotos/([^)]+)\)', uri, md)
    docs[id_] = {'path': path, 'title': title, 'md': md}

groups = [
    {'title': 'Motivos', 'note': 'Piezas sueltas que se usan solas o dentro de proyectos más grandes.', 'items': [
        {'id': 'hojas-texturizadas', 'name': 'Hojas texturizadas', 'level': 'Principiante', 'size': '7 × 4 cm', 'desc': 'Hoja en rombo con costillas, en tres verdes.'},
        {'id': 'poinsettia', 'name': 'Poinsettia', 'level': 'Intermedio', 'size': '7 – 15 cm', 'desc': 'Flor 3D en capas, mini de 2 capas y versión por pétalos.'},
        {'id': 'pina', 'name': 'Piña', 'level': 'Intermedio', 'size': '6 × 4,5 cm', 'desc': 'Cuerpo amigurumi con bobbles escalonados como escamas.'},
        {'id': 'bayas', 'name': 'Bayas', 'level': 'Principiante', 'size': '2 – 3 cm', 'desc': 'Bolitas rojas y crudas para hacer racimos.'},
        {'id': 'campana', 'name': 'Campana', 'level': 'Intermedio', 'size': '5 cm', 'desc': 'Con costillas y badajo de cuenta de madera.'},
        {'id': 'lazo', 'name': 'Lazo grande', 'level': 'Principiante', 'size': '18 cm', 'desc': 'Lazo verde con dos colas para la parte alta de la corona.'},
    ]},
    {'title': 'Adornos de árbol', 'note': 'Proyectos pequeños y terminados.', 'items': [
        {'id': 'mini-corona-bobbles', 'name': 'Mini corona de bobbles', 'level': 'Intermedio', 'size': '6,5 cm', 'desc': 'Con lazo de cordel y cuentas de madera, la del vídeo.'},
        {'id': 'campanas-nordicas', 'name': 'Campanas nórdicas', 'level': 'Avanzado', 'size': '10 × 8 cm', 'desc': 'Base con lazo o flor, malla dorada, hojas en cascada y colores joya.'},
    ]},
    {'title': 'Proyectos', 'note': 'Combinan varios motivos.', 'items': [
        {'id': 'corona-de-puerta', 'name': 'Corona de puerta', 'level': 'Intermedio', 'size': '35 cm', 'desc': 'Cantidades de cada pieza y orden de montaje.'},
    ]},
]

thumbs = {'hojas-texturizadas':'hojas.jpg','poinsettia':'poinsettia-detalle.jpg','pina':'pina.jpg','bayas':'bayas.jpg','campana':'campana.jpg','lazo':'corona-puerta-2.jpg','mini-corona-bobbles':'mini-corona.jpg','campanas-nordicas':'campanas-nordicas.jpg','corona-de-puerta':'corona-puerta.jpg'}
for g in groups:
    for it in g['items']:
        im = Image.open(f"{ROOT}/navidad/fotos/{thumbs[it['id']]}").convert('RGB')
        s = min(im.size); l=(im.width-s)//2; t=(im.height-s)//2
        im = im.crop((l,t,l+s,t+s)).resize((160,160), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf,'JPEG',quality=72,optimize=True)
        it['img'] = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

def js(o):
    return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')

t = open(f'{ROOT}/sitio/plantilla.html', encoding='utf-8').read()
body = t.replace('__DOCS__', js(docs)).replace('__GROUPS__', js(groups))

# index.html: documento completo para Vercel / GitHub Pages / abrir en el navegador
i = body.index('</style>') + len('</style>')
head, rest = body[:i], body[i:]
head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">', '')
page = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="theme-color" content="#1f4d3b">\n'
        '<link rel="manifest" href="manifest.webmanifest">\n'
        '<link rel="icon" href="icon-192.png">\n'
        '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
        + head + '\n<style>body{margin:0}img{max-width:100%}</style>\n</head>\n<body>\n' + rest + '\n</body>\n</html>\n')
open(f'{ROOT}/index.html', 'w', encoding='utf-8').write(page)
print('index.html', len(page), 'bytes')

# Opcional: python3 build_site.py fragmento.html  -> fragmento para publicar como Artifact de claude.ai
if len(sys.argv) > 1:
    open(sys.argv[1], 'w', encoding='utf-8').write(body)
    print(sys.argv[1], len(body), 'bytes')
