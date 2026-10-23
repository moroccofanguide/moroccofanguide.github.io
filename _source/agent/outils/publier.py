"""Publie site/ sur GitHub Pages (moroccofanguide/moroccofanguide.github.io) en UN seul commit :
ajoute ou modifie les fichiers changés. Ne supprime JAMAIS rien (un autre agent publie aussi sur ce dépôt).
Refuse de publier si le dépôt a changé depuis outils/.base-sha d'une façon que site/ ne reproduit pas
(lancer outils/synchro.py pour voir quoi reconstituer).
Usage : python3 -I outils/publier.py "message du commit"
"""
import base64, hashlib, json, os, sys, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import synchro

TOKEN = open('/srv/agent/.github-moveon-token').read().strip()
REPO = 'moroccofanguide/moroccofanguide.github.io'
AUTEUR = {'name': 'Morocco Fan Guide', 'email': 'webmaster@moroccofanguide.com'}  # identité des commits (domaine .com)
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')
MSG = sys.argv[1] if len(sys.argv) > 1 else 'Mise à jour du site'


def api(method, path, body=None):
    req = urllib.request.Request('https://api.github.com/repos/' + REPO + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization': 'Bearer ' + TOKEN, 'Accept': 'application/vnd.github+json',
                 'X-GitHub-Api-Version': '2022-11-28'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read(); return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read(); raise SystemExit(f'{method} {path} -> {e.code} {raw[:300]!r}')


_, ref = api('GET', '/git/ref/heads/main')
head = ref['object']['sha']
_, commit = api('GET', f'/git/commits/{head}')
_, tree = api('GET', f'/git/trees/{commit["tree"]["sha"]}?recursive=1')
remote = {t['path']: t['sha'] for t in tree['tree'] if t['type'] == 'blob'}

_, _, _, ailleurs, _ = synchro.etat()
base_head = synchro.api('/git/ref/heads/main')['object']['sha']
if base_head != head:
    raise SystemExit('Le dépôt a bougé pendant le contrôle : relancer.')

local = synchro.local_data()  # site généré + notre source sous _source/agent/

entries, changes = [], []
for path, data in sorted(local.items()):
    sha = hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()
    if remote.get(path) == sha:
        continue
    _, blob = api('POST', '/git/blobs', {'content': base64.b64encode(data).decode(), 'encoding': 'base64'})
    entries.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    changes.append(('modifié' if path in remote else 'ajouté') + ' ' + path)
bloque = sorted(p for p in ailleurs if p in local and remote.get(p) != hashlib.sha1(
    b'blob %d\0' % len(local[p]) + local[p]).hexdigest())
if bloque:
    raise SystemExit('PUBLICATION REFUSÉE : modifié dans le dépôt par ailleurs et pas reproduit ici '
                     '(lancer outils/synchro.py) : ' + ', '.join(bloque))
# Supprimés du dépôt s'ils ne sont plus produits ici : notre source et les fichiers de découverte (jamais les pages)
A_NOUS = ('_source/agent/', '.well-known/', '.nojekyll')
for path in sorted(set(remote) - set(local)):
    if path.startswith(A_NOUS):
        entries.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': None})
        changes.append('supprimé ' + path)
    else:
        print('présent seulement dans le dépôt (conservé) :', path)

if not entries:
    print('rien à publier')
    open(synchro.BASE_FILE, 'w').write(head)
    raise SystemExit(0)
_, new_tree = api('POST', '/git/trees', {'base_tree': commit['tree']['sha'], 'tree': entries})
_, new_commit = api('POST', '/git/commits', {'message': MSG, 'author': AUTEUR, 'tree': new_tree['sha'], 'parents': [head]})
api('PATCH', '/git/refs/heads/main', {'sha': new_commit['sha']})  # sans force : échoue si le dépôt a bougé
open(synchro.BASE_FILE, 'w').write(new_commit['sha'])
print('\n'.join(changes))
print('commit', new_commit['sha'][:7])

# Signale les pages nouvelles ou modifiées à IndexNow (Bing, Yandex, Seznam, Naver… ; Google ne l'utilise pas)
INDEXNOW_KEY = '771ca46f2c99484aadff63b91614f89d'
pages = sorted({'https://moroccofanguide.com/' + e['path'][:-len('index.html')]
                for e in entries if e['path'].endswith('index.html')})
if pages:
    body = {'host': 'moroccofanguide.com', 'key': INDEXNOW_KEY, 'urlList': pages,
            'keyLocation': f'https://moroccofanguide.com/{INDEXNOW_KEY}.txt'}
    try:
        req = urllib.request.Request('https://api.indexnow.org/indexnow', data=json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json; charset=utf-8'})
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f'IndexNow : {len(pages)} page(s) signalée(s), code {r.status}')
    except Exception as ex:
        print('IndexNow : échec (la publication, elle, est faite) :', ex)
