"""Sources de vécu pour les articles : chercher, enregistrer, vérifier.

Règle (instructions globales SEO) : un article ne se publie pas sans vécu.
  - soit l'apport de l'auteur dans contenu/vecu/<slug>.md (anecdote, prix constaté, conseil personnel),
  - soit au moins 2 témoignages concordants de voyageurs, de 2 sites différents, datés de moins de 36 mois.
  L'apport de l'auteur reste prioritaire : sans lui, l'article part en brouillon et l'agent le demande.

Usage :
  python3 -I outils/sources_vecu.py requetes "<sujet>" [--lang fr|en]
      Affiche les requêtes WebSearch à lancer (forums, Reddit, vidéos, avis). Ne contacte aucun serveur.
  python3 -I outils/sources_vecu.py ajouter <slug> --type <type> --url <url> --date AAAA-MM --resume "<ce qu'on en retient>" [--citation "<extrait court>"]
      Enregistre un témoignage dans contenu/sources/<slug>.json. Types : forum, reddit, social, video, avis, auteur.
  python3 -I outils/sources_vecu.py verifier <slug>
      Contrôle la règle ci-dessus. Code retour 0 = publiable, 1 = manque du vécu (brouillon + demande à l'auteur).
  python3 -I outils/sources_vecu.py liste <slug>
      Affiche les sources enregistrées.

Garde-fous appliqués par l'outil :
  - citation de 25 mots maximum (au-delà : reformuler, ne jamais recopier) ;
  - aucun pseudo, e-mail ou numéro de téléphone enregistré ;
  - un témoignage de voyageur est présenté comme tel dans l'article (« des voyageurs rapportent… », avec lien),
    jamais comme l'expérience de l'auteur.
"""
import datetime, json, os, re, sys
from urllib.parse import urlparse

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SOURCES = os.path.join(BASE, 'contenu', 'sources')
VECU = os.path.join(BASE, 'contenu', 'vecu')
TYPES = ('forum', 'reddit', 'social', 'video', 'avis', 'auteur')
MAX_MOTS = 25
MAX_MOIS = 36

REQUETES = {
    'fr': [
        '{s} avis forum voyage',
        '{s} site:voyageforum.com',
        '{s} site:routard.com forum',
        '{s} retour d\'expérience voyage Maroc',
        '{s} arnaque OR piège témoignage',
        '{s} prix payé 2025 OR 2026',
        '{s} site:reddit.com',
        '{s} site:youtube.com vlog',
    ],
    'en': [
        '{s} site:reddit.com/r/Morocco',
        '{s} site:reddit.com/r/travel',
        '{s} site:reddit.com/r/solotravel',
        '{s} tripadvisor forum',
        '{s} trip report',
        '{s} scam OR tourist trap experience',
        '{s} price paid 2025 OR 2026',
        '{s} site:youtube.com vlog',
    ],
}


def fichier(slug):
    if not re.fullmatch(r'[a-z0-9-]+', slug):
        sys.exit('slug invalide : lettres minuscules, chiffres et tirets uniquement')
    return os.path.join(SOURCES, slug + '.json')


def lire(slug):
    f = fichier(slug)
    return json.load(open(f, encoding='utf-8')) if os.path.exists(f) else []


def mois_depuis(date):
    a, m = map(int, date.split('-')[:2])
    t = datetime.date.today()
    return (t.year - a) * 12 + (t.month - m)


def requetes(args):
    if not args:
        sys.exit('sujet manquant')
    sujet = args[0]
    lang = args[args.index('--lang') + 1] if '--lang' in args else 'fr'
    print(f'Requêtes WebSearch pour « {sujet} » ({lang}). Lire les fils avec WebFetch, garder les plus récents.')
    for q in REQUETES[lang]:
        print('  ' + q.format(s=sujet))
    print('Ne pas utiliser : contenus derrière connexion (groupes Facebook privés), avis Google Maps ou TripAdvisor '
          'recopiés en masse. Lire, résumer, citer court, lier.')


def opt(args, nom, requis=True):
    if nom in args:
        return args[args.index(nom) + 1]
    if requis:
        sys.exit(f'option manquante : {nom}')
    return None


def ajouter(args):
    slug = args[0]
    t = opt(args, '--type')
    if t not in TYPES:
        sys.exit('type invalide : ' + ', '.join(TYPES))
    url = opt(args, '--url', requis=(t != 'auteur'))
    date = opt(args, '--date')
    if not re.fullmatch(r'\d{4}-\d{2}', date):
        sys.exit('date au format AAAA-MM')
    resume = opt(args, '--resume')
    citation = opt(args, '--citation', requis=False)
    texte = ' '.join(x for x in (resume, citation or '') if x)
    if re.search(r'[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d .-]{8,}\d|(^|\s)u/\w+|@\w{3,}', texte):
        sys.exit('refusé : pas de pseudo, e-mail ou numéro de téléphone dans les sources')
    if citation and len(citation.split()) > MAX_MOTS:
        sys.exit(f'citation trop longue ({len(citation.split())} mots, maximum {MAX_MOTS}) : reformuler')
    data = lire(slug)
    if url and any(x.get('url') == url for x in data):
        sys.exit('déjà enregistré : ' + url)
    data.append({'type': t, 'url': url, 'site': urlparse(url).netloc.replace('www.', '') if url else 'auteur',
                 'date': date, 'resume': resume, 'citation': citation,
                 'ajoute': datetime.date.today().isoformat()})
    os.makedirs(SOURCES, exist_ok=True)
    json.dump(data, open(fichier(slug), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'enregistré ({len(data)} source(s) pour {slug})')


def verifier(args):
    slug = args[0]
    data = lire(slug)
    vecu = os.path.join(VECU, slug + '.md')
    auteur = os.path.exists(vecu) and len(open(vecu, encoding='utf-8').read().split()) >= 15
    auteur = auteur or any(x['type'] == 'auteur' for x in data)
    recents = [x for x in data if x['type'] != 'auteur' and mois_depuis(x['date']) <= MAX_MOIS]
    sites = {x['site'] for x in recents}
    print(f'{slug} : apport de l\'auteur = {"oui" if auteur else "non"} ; '
          f'témoignages récents = {len(recents)} sur {len(sites)} site(s)')
    if auteur:
        print('OK : publiable (vérifier aussi que chaque fait est sourcé)')
        sys.exit(0)
    if len(recents) >= 2 and len(sites) >= 2:
        print('OK avec réserve : publiable avec les témoignages présentés comme tels, '
              'mais demander quand même l\'apport de l\'auteur (🟠) pour la prochaine mise à jour')
        sys.exit(0)
    print('MANQUE DE VÉCU : écrire en brouillon (contenu/brouillons/), ne pas publier, '
          f'demander à l\'auteur son expérience dans le rapport (🟠), à déposer dans contenu/vecu/{slug}.md')
    sys.exit(1)


def liste(args):
    for x in lire(args[0]):
        print(f"- [{x['type']}] {x['date']} {x['site']} : {x['resume']}" + (f" « {x['citation']} »" if x.get('citation') else '')
              + (f"\n  {x['url']}" if x.get('url') else ''))


if __name__ == '__main__':
    cmds = {'requetes': requetes, 'ajouter': ajouter, 'verifier': verifier, 'liste': liste}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])
