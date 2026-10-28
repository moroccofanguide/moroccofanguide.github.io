#!/usr/bin/env python3
"""Volumes et concurrence Google Ads (DataForSEO, données de Keyword Planner), Google France par défaut.
Usage :
  python3 -I outils/mots_cles.py volumes "mot 1" "mot 2" ...    (jusqu'à 1000 mots-clés, 1 requête)
  python3 -I outils/mots_cles.py idees "graine 1" "graine 2" ... (jusqu'à 20 graines, idées longue traîne, 1 requête)
  options : --en (Royaume-Uni, anglais) ; --min N (volume minimum affiché, défaut 10)
Chaque requête coûte environ 0,075 $ quel que soit le nombre de mots-clés : grouper. Résultats bruts dans donnees/.
concurrence = enchères Google Ads (LOW/MEDIUM/HIGH), pas la difficulté SEO."""
import base64, json, os, sys, time, urllib.request

CONF = '/srv/agent/.dataforseo-moveon.json'
API = 'https://api.dataforseo.com/v3/keywords_data/google_ads/'
ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

args = sys.argv[1:]
en = '--en' in args
mini = int(args[args.index('--min') + 1]) if '--min' in args else 10
args = [a for i, a in enumerate(args) if a not in ('--en', '--min') and (i == 0 or args[i - 1] != '--min')]
if len(args) < 2 or args[0] not in ('volumes', 'idees'):
    raise SystemExit(__doc__)
mode, mots = args[0], args[1:]

c = json.load(open(CONF))
auth = base64.b64encode(f'{c["login"]}:{c["password"]}'.encode()).decode()
corps = [{'keywords': mots, 'location_code': 2826 if en else 2250, 'language_code': 'en' if en else 'fr'}]
url = API + ('search_volume' if mode == 'volumes' else 'keywords_for_keywords') + '/live'
req = urllib.request.Request(url, data=json.dumps(corps).encode(),
                             headers={'Authorization': 'Basic ' + auth, 'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
except urllib.error.HTTPError as e:
    try:
        msg = json.load(e).get('status_message')
    except ValueError:
        msg = ''
    raise SystemExit(f'Refus de DataForSEO ({e.code}) : {msg}')
t = d['tasks'][0]
if t.get('status_code') != 20000:
    raise SystemExit(f'Erreur DataForSEO : {t.get("status_code")} {t.get("status_message")}')

os.makedirs(os.path.join(ICI, 'donnees'), exist_ok=True)
nom = os.path.join(ICI, 'donnees', f'{time.strftime("%Y%m%d-%H%M%S")}-{mode}{"-en" if en else ""}.json')
json.dump({'mots': mots, 'resultat': t.get('result') or []}, open(nom, 'w'), ensure_ascii=False)

lignes = [r for r in (t.get('result') or []) if (r.get('search_volume') or 0) >= mini]
lignes.sort(key=lambda r: -(r.get('search_volume') or 0))
for r in lignes:
    print(f'{r.get("search_volume") or 0:>7} | {r.get("competition") or "-":<6} | {r.get("cpc") or 0:>5} | {r["keyword"]}')
print(f'{len(lignes)} ligne(s) affichée(s) sur {len(t.get("result") or [])} | coût {d.get("cost")} $ | {nom}')
