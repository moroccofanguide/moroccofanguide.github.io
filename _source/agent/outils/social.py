"""Publie les articles du site sur la Page Facebook « Morocco Fan Guide » (Graph API), un article par appel.
Accès : /srv/agent/.meta-moveon.json (jeton de Page sans expiration, jamais affiché ni copié dans le dépôt).
Déjà publiés : ../social-publies.json (hors dépôt GitHub), pour ne jamais republier le même article.
Usage :
  python3 -I outils/social.py              -> vérifie l'accès à la Page (lecture seule)
  python3 -I outils/social.py --publier    -> publie le prochain article pas encore partagé (lien)
  python3 -I outils/social.py --natif <chemin article, ex. /desert-agafay/> --texte-fichier <f> [--lien-commentaire] [--essai]
      -> post natif : photo de l'article + conseil complet (texte du fichier) + crédit photo ;
         lien du guide en 1er commentaire seulement avec --lien-commentaire (1 post natif sur 3).
L'article choisi : le plus récent non partagé, en alternant FR et EN (la langue la moins partagée d'abord).
"""
import json, os, re, sys, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PROJET = os.path.join(HERE, '..')
CONF = json.load(open('/srv/agent/.meta-moveon.json'))
DEJA = os.path.join(PROJET, 'social-publies.json')
DOMAIN = 'https://moroccofanguide.com'
G = 'https://graph.facebook.com/v23.0/'
INTRO = {'fr': 'Nouveau sur le guide :', 'en': 'New on the guide:'}


def graph(method, path, **q):
    q['access_token'] = CONF['page_token']
    data = urllib.parse.urlencode(q).encode()
    url = G + path + ('' if method == 'POST' else '?' + data.decode())
    req = urllib.request.Request(url, data=data if method == 'POST' else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        err = json.load(e).get('error', {})
        raise SystemExit(f'Refus de Meta ({e.code}) : {err.get("message")}')


def articles():
    out = []
    for lang in ('fr', 'en'):
        d = os.path.join(PROJET, 'contenu', lang)
        for f in sorted(os.listdir(d)):
            m = re.match(r'<!--meta (\{.*?\}) -->', open(os.path.join(d, f), encoding='utf-8').read())
            meta = json.loads(m.group(1))
            if meta.get('type') == 'article':
                out.append(dict(meta, lang=lang, url=DOMAIN + meta['path']))
    return out


def prochain(deja):
    reste = [a for a in articles() if a['url'] not in deja]
    if not reste:
        return None
    compte = {l: sum(1 for x in deja.values() if x.get('lang') == l) for l in ('fr', 'en')}
    reste.sort(key=lambda a: (compte[a['lang']], -int(a.get('published', '0').replace('-', '') or 0), a['path']))
    return reste[0]


def arg(nom):
    return sys.argv[sys.argv.index(nom) + 1] if nom in sys.argv else None


def natif():
    import datetime
    chemin, essai = arg('--natif'), '--essai' in sys.argv
    a = next((x for x in articles() if x['path'] == chemin), None)
    if not a or not a.get('image'):
        raise SystemExit(f'Article introuvable ou sans image : {chemin}')
    texte = open(arg('--texte-fichier'), encoding='utf-8').read().strip()
    if len(texte) < 300:
        raise SystemExit('Conseil trop court (300 caractères min) : un post natif apporte un conseil complet.')
    if re.search(r'https?://', texte):
        raise SystemExit('Pas de lien dans la légende : le lien va en 1er commentaire (--lien-commentaire).')
    i = json.load(open(os.path.join(HERE, 'images.json'), encoding='utf-8'))[a['image']]
    msg = f"{texte}\n\nPhoto : {i['author']}, {i['license']}, {i.get('site', 'Wikimedia Commons')}"
    deja = json.load(open(DEJA)) if os.path.exists(DEJA) else {}
    cle = 'natif:' + chemin
    if cle in deja:
        raise SystemExit(f'Post natif déjà publié pour {chemin} le {deja[cle]["date"]}')
    print('Image :', DOMAIN + i['file'], '| lien en commentaire :', '--lien-commentaire' in sys.argv)
    print('Légende :\n' + msg)
    if essai:
        return
    r = graph('POST', CONF['page_id'] + '/photos', url=DOMAIN + i['file'], message=msg)
    post = r.get('post_id') or r.get('id')
    entree = {'lang': a['lang'], 'post_id': post, 'date': datetime.date.today().isoformat(), 'natif': True}
    if '--lien-commentaire' in sys.argv:
        c = graph('POST', post + '/comments', message=a['url'])
        entree['commentaire'] = c.get('id')
    deja[cle] = entree
    json.dump(deja, open(DEJA, 'w'), ensure_ascii=False, indent=1)
    print('Publié (natif) :', chemin, '-> post', post, '| commentaire', entree.get('commentaire'))


if __name__ == '__main__':
    if '--natif' in sys.argv:
        natif()
        sys.exit(0)
    page = graph('GET', CONF['page_id'], fields='name,link,followers_count')
    print('Page :', page.get('name'), '-', page.get('followers_count'), 'abonnés')
    if '--publier' not in sys.argv:
        sys.exit(0)
    deja = json.load(open(DEJA)) if os.path.exists(DEJA) else {}
    a = prochain(deja)
    if not a:
        print('Tous les articles sont déjà partagés sur Facebook.')
        sys.exit(0)
    msg = f"{INTRO[a['lang']]} {a['title']}\n\n{a['description']}"
    r = graph('POST', CONF['page_id'] + '/feed', message=msg, link=a['url'])
    deja[a['url']] = {'lang': a['lang'], 'post_id': r.get('id'), 'date': __import__('datetime').date.today().isoformat()}
    json.dump(deja, open(DEJA, 'w'), ensure_ascii=False, indent=1)
    print('Publié sur Facebook :', a['url'], '-> post', r.get('id'))
