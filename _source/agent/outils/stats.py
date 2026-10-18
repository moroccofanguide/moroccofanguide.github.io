"""Statistiques Travelpayouts du projet moveon (lecture seule ; le jeton n'est jamais affiché).

Usage : python3 -I outils/stats.py [jours]   (défaut : 7 jours)
Affiche le solde, puis par partenaire et par type d'événement (init_tool = chargement du script sur une page,
redirect = clic vers un partenaire, autres = réservations) : nombre, gains en cours et payés, appareils, pages.
install_type « integration_background » = popunder ; « link_switcher » = lien converti ; vide = chargement.
"""
import collections, datetime, json, sys, urllib.request

TOKEN = open('/srv/agent/.travelpayouts-moveon-token').read().strip()
API = 'https://api.travelpayouts.com'


def call(path, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                                 headers={'X-Access-Token': TOKEN, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=30))


jours = int(sys.argv[1]) if len(sys.argv) > 1 else 7
depuis = (datetime.date.today() - datetime.timedelta(days=jours)).isoformat()
print('Solde :', call('/finance/v2/get_user_balance')['balance'])
champs = ['campaign_name_en', 'type', 'state', 'install_type', 'processing_profit_usd', 'paid_profit_usd',
          'price_usd', 'page_url', 'user_device_type', 'user_country', 'is_bot', 'date']
lignes, offset = [], 0
while True:
    r = call('/statistics/v1/execute_query', {'fields': champs, 'filters': [{'field': 'date', 'op': 'ge', 'value': depuis}],
                                               'sort': [{'field': 'date', 'order': 'desc'}], 'offset': offset, 'limit': 1000})['results']
    lignes += r
    if len(r) < 1000:
        break
    offset += 1000
humains = [x for x in lignes if not x['is_bot']]
print(f'Depuis le {depuis} : {len(lignes)} événements, dont {len(lignes) - len(humains)} robots (exclus ci-dessous)')
groupes = collections.defaultdict(list)
for x in humains:
    groupes[(x['campaign_name_en'], x['type'], x['install_type'] or '-')].append(x)
for (marque, typ, inst), xs in sorted(groupes.items(), key=lambda g: -len(g[1])):
    gain = sum(float(x['processing_profit_usd']) + float(x['paid_profit_usd']) for x in xs)
    print(f'- {marque} | {typ} | {inst} : {len(xs)} ; gains {gain:.2f} $ ; '
          f'{dict(collections.Counter(x["user_device_type"] for x in xs))}')
pages = collections.Counter(x['page_url'] for x in humains if x['type'] == 'init_tool')
print('Pages vues (chargements du script) :', dict(pages.most_common(10)))
print('Pays :', dict(collections.Counter(x['user_country'] for x in humains).most_common(8)))
print('Par jour :', dict(sorted(collections.Counter(x['date'] for x in humains).items())))
