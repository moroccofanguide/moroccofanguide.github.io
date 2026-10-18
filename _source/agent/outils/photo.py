"""Ajoute une photo libre de Wikimedia Commons au site (static/img/ + outils/images.json).

Usage : python3 -I outils/photo.py <clé> "<titre exact du fichier Commons, sans File:>" "<alt FR>" "<alt EN>"
        python3 -I outils/photo.py --chercher "<mots-clés>"   (liste des photos « Quality images » avec licence)
La clé (a-z, 0-9, -) s'utilise ensuite dans les métadonnées d'un article : "image": "<clé>".
Licences acceptées : CC0, domaine public, CC BY, CC BY-SA (le crédit est affiché automatiquement).
"""
import json, os, re, sys, urllib.parse, urllib.request

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
API = 'https://commons.wikimedia.org/w/api.php?'
UA = {'User-Agent': 'MoroccoFanGuide/1.0 (https://moroccofanguide.com; image selection)'}
LIBRES = re.compile(r'^(CC0|Public domain|CC BY(-SA)? \d\.\d)$', re.I)


def api(**p):
    p['format'] = 'json'
    req = urllib.request.Request(API + urllib.parse.urlencode(p), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=30))


def meta(ii):
    m = ii.get('extmetadata', {})
    g = lambda k: re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', m.get(k, {}).get('value', ''))).strip()
    return g('LicenseShortName'), g('Artist'), g('LicenseUrl')


def chercher(q):
    """Photos labellisées « Quality images » d'abord [QI], puis toutes les autres [--]."""
    vus = set()
    for label, s in (('QI', f'{q} incategory:Quality_images'), ('--', q)):
        d = api(action='query', generator='search', gsrnamespace=6, gsrlimit=12,
                gsrsearch=s, prop='imageinfo', iiprop='size|extmetadata')
        for pg in d.get('query', {}).get('pages', {}).values():
            ii = pg['imageinfo'][0]
            if pg['title'] in vus or not pg['title'].lower().endswith(('.jpg', '.jpeg')):
                continue
            vus.add(pg['title'])
            lic, art, _ = meta(ii)
            ok = 'OK' if LIBRES.match(lic) and ii['width'] >= ii['height'] >= 800 else 'non'
            print(f'{ok} [{label}] {pg["title"][5:]} | {ii["width"]}x{ii["height"]} | {lic} | {art[:40]}')


def ajouter(cle, titre, alt_fr, alt_en):
    if not re.fullmatch(r'[a-z0-9-]+', cle):
        raise SystemExit('clé invalide (a-z, 0-9, -)')
    path = os.path.join(BASE, 'outils', 'images.json')
    images = json.load(open(path, encoding='utf-8'))
    if cle in images:
        raise SystemExit(f'clé déjà utilisée : {cle}')
    files = {}
    for w, suffixe in ((960, ''), (500, '-500')):
        d = api(action='query', titles='File:' + titre, prop='imageinfo', iiprop='url|extmetadata', iiurlwidth=w)
        pg = next(iter(d['query']['pages'].values()))
        if 'imageinfo' not in pg:
            raise SystemExit(f'fichier introuvable sur Commons : {titre}')
        ii = pg['imageinfo'][0]
        lic, art, lic_url = meta(ii)
        if not LIBRES.match(lic):
            raise SystemExit(f'licence refusée : {lic}')
        data = urllib.request.urlopen(urllib.request.Request(ii['thumburl'], headers=UA), timeout=60).read()
        open(os.path.join(BASE, 'static', 'img', f'{cle}{suffixe}.jpg'), 'wb').write(data)
        files[w] = (ii, len(data))
    ii = files[960][0]
    images[cle] = {'file': f'/img/{cle}.jpg', 'small': f'/img/{cle}-500.jpg', 'w': ii['thumbwidth'], 'h': ii['thumbheight'],
                   'alt_fr': alt_fr, 'alt_en': alt_en, 'author': art, 'license': lic,
                   'license_url': lic_url.replace('http://', 'https://'), 'source': ii['descriptionurl']}
    json.dump(images, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{cle} ajoutée : {lic}, {art}, {files[960][1] // 1024} Ko + {files[500][1] // 1024} Ko')


if len(sys.argv) == 3 and sys.argv[1] == '--chercher':
    chercher(sys.argv[2])
elif len(sys.argv) == 5:
    ajouter(*sys.argv[1:])
else:
    raise SystemExit(__doc__)
