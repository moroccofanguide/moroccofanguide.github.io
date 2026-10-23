"""« git pull » du projet : compare le site généré (site/) au dépôt GitHub, car un autre agent publie aussi dessus.
À lancer après `python3 -I outils/build.py` et avant `publier.py`.
Usage : python3 -I outils/synchro.py

Référence : outils/.base-sha = dernier commit du dépôt que notre site/ reproduit (écrit par publier.py et ici).
- Fichier changé dans le dépôt depuis cette référence (ou référence absente) et différent chez nous :
  - fichier non HTML (llms.txt, script, image…) : téléchargé dans static/ (le dépôt gagne), relancer build.py ;
  - page HTML : À RECONSTITUER dans contenu/ à partir de la page en ligne, puis relancer build.py et synchro.py.
- Fichier changé seulement chez nous : c'est notre travail, publier.py l'enverra.
Code retour 0 = rien ne bloque la publication ; 1 = pages à reconstituer (publier.py refusera de publier).
Si tout est identique au dépôt, la référence est avancée sur le dernier commit.
Contrôle de pertes, toujours fait : page, entrée du sitemap ou lien interne du dépôt absent chez nous, balise Pinterest.
`python3 -I outils/synchro.py --accepter` : une fois les pages reprises dans contenu/ et les écarts restants vérifiés
(volontaires : ordre, temps de lecture…), avance la référence sur le dépôt ; refusé s'il reste une perte.
"""
import base64, hashlib, json, os, sys, urllib.request

TOKEN = open('/srv/agent/.github-moveon-token').read().strip()
REPO = 'moroccofanguide/moroccofanguide.github.io'
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, '..', 'site')
STATIC = os.path.join(HERE, '..', 'static')
BASE_FILE = os.path.join(HERE, '.base-sha')
PROJET = os.path.join(HERE, '..')
# Notre source, publiée dans le dépôt sous _source/agent/ (dépôt public : jamais de secret ni de notes perso dedans)
SOURCE = '_source/agent/'
SOURCE_DIRS = ['contenu', 'outils', 'static']
SOURCE_FILES = ['plan-editorial.md', 'README.md']
# Jamais publiés (dépôt public) : consignes internes de l'agent, notes de vécu de l'auteur, brouillons, sauvegardes
SOURCE_SKIP = ('static/img/', 'static/fonts/', 'outils/__pycache__/', 'outils/.base-sha',
               'outils/routine-quotidienne.md', 'contenu/vecu/', 'contenu/brouillons/')


def api(path):
    req = urllib.request.Request('https://api.github.com/repos/' + REPO + path,
        headers={'Authorization': 'Bearer ' + TOKEN, 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def tree(commit_sha):
    t = api('/git/trees/' + api('/git/commits/' + commit_sha)['tree']['sha'] + '?recursive=1')
    return {x['path']: x['sha'] for x in t['tree'] if x['type'] == 'blob'}


def blob_sha(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def local_path(p):
    """Fichier local correspondant à un chemin du dépôt (None si ce chemin n'est pas à nous)."""
    if p.startswith(SOURCE):
        return os.path.join(PROJET, p[len(SOURCE):])
    if p.startswith('_source/'):
        return None  # source d'un autre agent : on la lit, on n'y touche pas
    return os.path.join(SITE, p)


def local_data():
    """{chemin dans le dépôt: contenu} : site généré + notre source sous _source/agent/."""
    out = {}
    for dirpath, _, files in os.walk(SITE):
        for f in files:
            full = os.path.join(dirpath, f)
            out[os.path.relpath(full, SITE)] = open(full, 'rb').read()
    rel = [os.path.relpath(os.path.join(d, f), PROJET) for top in SOURCE_DIRS
           for d, _, fs in os.walk(os.path.join(PROJET, top)) for f in fs] + SOURCE_FILES
    for r in sorted(rel):
        if not r.startswith(SOURCE_SKIP) and not r.endswith('.pyc') and '.bak' not in r:
            out[SOURCE + r] = open(os.path.join(PROJET, r), 'rb').read()
    return out


def local_files():
    return {p: blob_sha(d) for p, d in local_data().items()}


def etat():
    """Renvoie (head, distant, base, changés_ailleurs, local) ; changés_ailleurs = chemins modifiés dans le dépôt
    depuis la référence (tous les chemins si la référence est absente)."""
    head = api('/git/ref/heads/main')['object']['sha']
    remote = tree(head)
    base = open(BASE_FILE).read().strip() if os.path.exists(BASE_FILE) else None
    if base == head:
        ailleurs = set()
    elif base:
        old = tree(base)
        ailleurs = {p for p in set(old) | set(remote) if old.get(p) != remote.get(p)}
    else:
        ailleurs = set(remote)
    return head, remote, base, ailleurs, local_files()


def conflits(remote, ailleurs, local):
    """Chemins changés dans le dépôt depuis la référence et que nous ne reproduisons pas (hors source des autres)."""
    return sorted(p for p in ailleurs if remote.get(p) != local.get(p) and local_path(p))


def pertes(remote):
    """Ce que notre régénération ferait disparaître du site en ligne."""
    import re
    out = []
    def lire(p, ici):
        if ici:
            f = os.path.join(SITE, p)
            return open(f, encoding='utf-8').read() if os.path.exists(f) else None
        return base64.b64decode(api('/git/blobs/' + remote[p])['content']).decode('utf-8')
    for p in sorted(remote):
        if p.startswith('_source/') or not (p.endswith('.html') or p == 'sitemap.xml'):
            continue
        ici = lire(p, True)
        if ici is None:
            out.append('page absente : ' + p)
            continue
        la = lire(p, False)
        for motif, quoi in ((r'<loc>(.*?)</loc>', 'entrée du sitemap'), (r'href="(/[^"#]*)"', 'lien')):
            for x in sorted(set(re.findall(motif, la)) - set(re.findall(motif, ici))):
                out.append(f'{quoi} disparue dans {p} : {x}')
        if 'p:domain_verify' in la and 'p:domain_verify' not in ici:
            out.append('balise Pinterest disparue : ' + p)
    return out


if __name__ == '__main__':
    head, remote, base, ailleurs, local = etat()
    perdus = pertes(remote)
    for x in perdus:
        print('PERTE :', x)
    if '--accepter' in sys.argv:
        if perdus:
            sys.exit('Référence NON avancée : corriger les pertes ci-dessus.')
        open(BASE_FILE, 'w').write(head)
        print('Référence avancée sur', head[:7], ': les écarts restants sont acceptés comme notre version.')
        sys.exit(0)
    print(f'Dépôt : {head[:7]} ; référence locale : {base[:7] if base else "aucune"}')
    a_reconstituer, telecharges = [], []
    for p in conflits(remote, ailleurs, local):
        if p not in remote:
            print('supprimé dans le dépôt (à supprimer aussi de contenu/ ou static/ si voulu) :', p)
            continue
        if p.endswith('.html') and not p.startswith(SOURCE):
            a_reconstituer.append(p)
            continue
        if p == 'sitemap.xml':
            a_reconstituer.append(p + ' (généré : ajouter les pages manquantes dans contenu/)')
            continue
        data = base64.b64decode(api('/git/blobs/' + remote[p])['content'])
        dest = local_path(p) if p.startswith(SOURCE) else os.path.join(STATIC, p)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, 'wb').write(data)
        telecharges.append(p)
    for p in telecharges:
        print('téléchargé :', p, '→', os.path.relpath(local_path(p) if p.startswith(SOURCE) else os.path.join(STATIC, p), PROJET))
    for p in a_reconstituer:
        print('À RECONSTITUER dans contenu/ (page modifiée ailleurs) :', p)
    if telecharges:
        print('→ relancer build.py puis synchro.py')
    nos_changements = sorted(p for p in local if local[p] != remote.get(p) and p not in ailleurs)
    print(f'{len(nos_changements)} fichier(s) changé(s) seulement chez nous (à publier)', nos_changements[:10])
    if not a_reconstituer and not telecharges and not perdus:
        open(BASE_FILE, 'w').write(head)
        print('OK : site/ reproduit tout ce qui a été publié ailleurs ; référence =', head[:7])
        sys.exit(0)
    sys.exit(1)
