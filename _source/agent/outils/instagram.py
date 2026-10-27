"""Publie les articles du site sur le compte Instagram « moroccofanguide » (Instagram API with Instagram Login), un par appel.
Accès : /srv/agent/.instagram-moveon.json (jeton IGAA de 60 jours, installé et renouvelé par
/srv/agent/depot/moveon-jeton-instagram.py, jamais affiché ni copié dans le dépôt).
Déjà publiés : ../instagram-publies.json (hors dépôt GitHub), pour ne jamais republier le même article.
Usage :
  python3 -I outils/instagram.py              -> vérifie l'accès au compte (lecture seule)
  python3 -I outils/instagram.py --publier    -> publie la photo du prochain article pas encore partagé
Même choix d'article que social.py. Le lien n'est pas cliquable dans une légende Instagram : « lien dans la bio ».
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from social import DOMAIN, PROJET, prochain  # noqa: E402

CONF = json.load(open('/srv/agent/.instagram-moveon.json'))
DEJA = os.path.join(PROJET, 'instagram-publies.json')
IMAGES = json.load(open(os.path.join(HERE, 'images.json')))
G = 'https://graph.instagram.com/v26.0/'
BIO = {'fr': 'Le guide complet : lien dans la bio.', 'en': 'Full guide: link in bio.'}
TAGS = {'fr': '#Maroc #VoyageMaroc #Marrakech', 'en': '#Morocco #MoroccoTravel #Marrakech'}


def graph(method, path, **q):
    q['access_token'] = CONF['token']
    data = urllib.parse.urlencode(q).encode()
    url = G + path + ('' if method == 'POST' else '?' + data.decode())
    req = urllib.request.Request(url, data=data if method == 'POST' else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        err = json.load(e).get('error', {})
        raise SystemExit(f'Refus d\'Instagram ({e.code}) : {err.get("message")}')


if __name__ == '__main__':
    me = graph('GET', 'me', fields='user_id,username,followers_count,media_count')
    print('Compte :', me.get('username'), '-', me.get('followers_count'), 'abonnés,',
          me.get('media_count'), 'publications | jeton valable jusqu\'au', CONF.get('expire'))
    if '--publier' not in sys.argv:
        sys.exit(0)
    deja = json.load(open(DEJA)) if os.path.exists(DEJA) else {}
    a = prochain(deja)
    if not a:
        print('Tous les articles sont déjà partagés sur Instagram.')
        sys.exit(0)
    img = IMAGES[a['image']]
    credit = f"Photo : {img['author']}, {img['license']}" if a['lang'] == 'fr' else f"Photo: {img['author']}, {img['license']}"
    legende = f"{a['title']}\n\n{a['description']}\n\n{BIO[a['lang']]}\n\n{credit}\n\n{TAGS[a['lang']]}"
    uid = str(CONF['user_id'])
    c = graph('POST', uid + '/media', image_url=DOMAIN + img['file'], caption=legende)
    for _ in range(12):
        etat = graph('GET', c['id'], fields='status_code').get('status_code')
        if etat == 'FINISHED':
            break
        if etat in ('ERROR', 'EXPIRED'):
            raise SystemExit(f'Image refusée par Instagram ({etat}) : {img["file"]}')
        time.sleep(5)
    else:
        raise SystemExit('Image toujours en traitement après 60 s : rien publié')
    r = graph('POST', uid + '/media_publish', creation_id=c['id'])
    lien = graph('GET', r['id'], fields='permalink').get('permalink')
    deja[a['url']] = {'lang': a['lang'], 'media_id': r.get('id'), 'permalink': lien,
                      'date': __import__('datetime').date.today().isoformat()}
    json.dump(deja, open(DEJA, 'w'), ensure_ascii=False, indent=1)
    print('Publié sur Instagram :', a['url'], '->', lien)
