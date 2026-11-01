"""Commentaires des Pages Facebook moveon (Morocco Fan Guide, Humour, Lovely Pets) : liste et réponse.
Jetons lus dans /srv/agent/.meta-moveon.json et /srv/agent/.meta-pages-perso.json, jamais affichés.
Usage :
  python3 -I outils/commentaires.py                      -> commentaires des 3 derniers jours sans réponse de la Page
  python3 -I outils/commentaires.py --repondre <id_commentaire> --texte "<réponse>"
"""
import datetime, json, sys, urllib.error, urllib.parse, urllib.request

G = 'https://graph.facebook.com/v23.0/'
m = json.load(open('/srv/agent/.meta-moveon.json'))
PAGES = {m['page_id']: ('Morocco Fan Guide', m['page_token'])}
for pid, v in json.load(open('/srv/agent/.meta-pages-perso.json')).items():
    PAGES[pid] = (v['page_name'], v['page_token'])


def graph(tok, path, post=None, **q):
    q['access_token'] = tok
    data = urllib.parse.urlencode(dict(q, **(post or {}))).encode()
    url = G + path + ('' if post else '?' + data.decode())
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data if post else None), timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f'Refus de Meta ({e.code}) : {json.load(e).get("error", {}).get("message")}')


def lister():
    depuis = int((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)).timestamp())
    total = 0
    for pid, (nom, tok) in PAGES.items():
        posts = graph(tok, pid + '/posts', since=depuis - 30 * 86400, limit=40,
                      fields='id,comments.limit(50){id,from,message,created_time,comments.limit(20){from}}')
        for p in posts.get('data', []):
            for c in p.get('comments', {}).get('data', []):
                if c.get('from', {}).get('id') == pid:
                    continue
                t = datetime.datetime.strptime(c['created_time'], '%Y-%m-%dT%H:%M:%S%z').timestamp()
                repondu = any(r.get('from', {}).get('id') == pid for r in c.get('comments', {}).get('data', []))
                if t >= depuis and not repondu:
                    total += 1
                    print(f"{nom} | {c['id']} | {c['created_time']} | {c.get('message', '')[:200]!r}")
    print(f'{total} commentaire(s) sans réponse de la Page (3 derniers jours).')


def repondre(cid, texte):
    pid = cid.split('_')[0]
    for p, (nom, tok) in PAGES.items():
        try:
            r = graph(tok, cid + '/comments', post={'message': texte})
            print('Réponse publiée :', nom, r.get('id'))
            return
        except SystemExit as e:
            dernier = e
    raise dernier


if __name__ == '__main__':
    if '--repondre' in sys.argv:
        repondre(sys.argv[sys.argv.index('--repondre') + 1], sys.argv[sys.argv.index('--texte') + 1])
    else:
        lister()
