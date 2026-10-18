# _source/agent : source complète du site (générateur unique)

Ce dossier n'est pas publié sur le site (Jekyll ignore les dossiers en « _ » : ne jamais créer de `.nojekyll`).
Le dépôt est public sur GitHub : aucun secret ni note personnelle ici.

Depuis le 2026-10-18, **toutes les pages du site** sont générées par `outils/build.py` à partir de `contenu/` :
y compris les 8 pages de `_source/claude/` (Marrakech la nuit, Maroc sûr, Taxis avec l'outil « Ce prix est-il normal ? »,
Prix au Maroc, FR + EN), reprises telles quelles dans `contenu/`. `_source/claude/build_all.py` n'est plus nécessaire :
le relancer après une régénération par build.py n'est pas utile et peut créer des écarts.

## Contenu
- `contenu/fr|en/*.html` : un fichier par page. Première ligne : métadonnées JSON (`path`, `alt` = traduction, `type`
  home|article, `title` = h1, `seo_title` = <title>, `description`, `crumb` = rubrique, `short` = libellé des cartes et
  du pied de page, `image` = clé de `outils/images.json`, `published`, `updated`), puis le corps HTML de `<main>`.
- `outils/build.py` : génère tout le site dans `site/` (en-tête, balise Pinterest, script Travelpayouts 586964,
  JSON-LD Article + FAQPage tiré de la section `id="faq"`, cartes d'accueil, pied de page, sitemap).
- `static/` : fichiers copiés tels quels (`llms.txt`, `robots.txt`, `CNAME`, `404.html`, `style.css`, images, polices).
- `outils/synchro.py`, `outils/publier.py` : outils de l'agent quotidien (le jeton n'est pas dans le dépôt).

## Méthode commune
1. Récupérer le dépôt (`git pull`).
2. Modifier `_source/agent/contenu/` (nouvel article : un fichier FR et un EN avec `alt` croisés ; mettre aussi à jour
   `static/llms.txt`).
3. Générer : depuis `_source/agent/`, `python3 outils/build.py` écrit dans `_source/agent/site/` ; copier ce dossier à la
   racine du dépôt (sans supprimer `_source/`).
4. Committer la source et le site dans le même commit.
