# _source/claude : sources des pages publiées par Claude (session mobile)

Ce dossier n'est pas publié : Jekyll (GitHub Pages) ignore les dossiers commençant par « _ ».
Ne pas créer de fichier `.nojekyll` à la racine, sinon ce dossier deviendrait public.

## Ce que contient ce dossier

- `content/` : le corps HTML (contenu de `<main>`) de chaque article, en FR et en EN.
  - `night_*` : Marrakech la nuit (`/marrakech-la-nuit-securite/`, `/en/is-marrakech-safe-at-night/`)
  - `safe_*` : Le Maroc est-il sûr ? (`/maroc-pays-sur/`, `/en/is-morocco-safe/`)
  - `taxi_*` : Taxis au Maroc, avec l'outil « Ce prix est-il normal ? » (`/taxis-maroc/`, `/en/taxis-in-morocco/`)
  - `prix_*` : Prix au Maroc (`/prix-maroc/`, `/en/morocco-prices/`)
- `build_all.py` : génère ces 8 pages et met à jour les éléments partagés.
- `make_tool.py` : génère le bloc de l'outil taxi (`content/tool_fr.html`, `content/tool_en.html`), à recopier dans `taxi_*.html`.

## Ce que fait build_all.py

Il n'a pas de gabarit propre : il prend comme modèle les pages déjà publiées `desert-agafay/index.html` (FR) et `en/agafay-desert/index.html` (EN), puis pour chaque article :

- remplace `<title>`, meta description, canonical, hreflang, Open Graph, JSON-LD (Article + FAQPage) ;
- remplace l'en-tête d'article, l'image principale (crédits Wikimedia) et le `<main>` ;
- ajoute ou rafraîchit le lien de l'article dans le pied de page de toutes les pages, la carte en page d'accueil FR/EN et l'entrée du sitemap.

Il échoue volontairement si la balise de vérification Pinterest est absente du gabarit.

Utilisation, depuis la racine du dépôt :

    python3 -I _source/claude/build_all.py "$PWD"

## Limites à connaître

- Le générateur de l'agent quotidien n'est pas dans ce dossier. Les autres pages du site (accueil, Agafay, excursions, Que faire à Marrakech, traversée en bateau) viennent de lui.
- Si ce générateur régénère l'accueil, les pieds de page ou le sitemap, il doit conserver les 8 pages ci-dessus, leurs cartes, leurs liens et leurs entrées de sitemap, ainsi que `llms.txt` et la balise `p:domain_verify`.
- Les tableaux de prix et les repères locaux viennent d'Abdallah (octobre 2026) ; les sources externes sont citées dans les articles.

## Méthode de travail commune

1. `git pull` avant toute modification.
2. Modifier la source dans `_source/`.
3. Régénérer le site.
4. Committer la source et les pages générées dans le même commit.
5. À chaque nouvel article : sitemap.xml, llms.txt, page d'accueil FR/EN, pieds de page.
