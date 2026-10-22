"""Génère site/ à partir de contenu/<langue>/*.html et static/.

Chaque fichier de contenu commence par un commentaire de métadonnées JSON :
<!--meta {"path": "/slug/", "title": "...", "description": "...", "alt": "/en/slug/",
          "type": "home|article", "updated": "2026-10-15", "crumb": "Venir au Maroc", "image": "jemaa"} -->
suivi du HTML de la page (sans en-tête ni pied de page).
"image" : clé de outils/images.json (photo libre de droits, crédit affiché automatiquement).
Dans le corps : [[img:clé]] insère une photo, [[articles]] la liste des articles de la langue (accueil).
Usage : python3 -I outils/build.py
"""
import hashlib, html, json, os, re, shutil

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SITE = os.path.join(BASE, 'site')
DOMAIN = 'https://moroccofanguide.com'
IMAGES = json.load(open(os.path.join(BASE, 'outils', 'images.json'), encoding='utf-8'))
# Photo par défaut d'un article sans clé "image", selon sa rubrique (crumb)
DEFAULT_IMG = {'Marrakech': 'marrakech', 'Venir au Maroc': 'ferry', 'Getting there': 'ferry'}
DRIVE = '''  <script nowprocket data-noptimize="1" data-cfasync="false" data-wpfc-render="false" seraph-accel-crit="1" data-no-defer="1" data-cmp-ab="2">
    (function () {
        var script = document.createElement("script");
        script.async = 1;
        script.setAttribute("data-cmp-ab","2");
        script.src = 'https://emrld.ltd/NTg2OTY0.js?t=586964';
        document.head.appendChild(script);
    })();
  </script>
  <script src="https://analytics.ahrefs.com/analytics.js" data-key="boM5zPeFGd5q5gQU6rGUxA" async></script>
'''
T = {
    'fr': {
        'home': '/', 'skip': 'Aller au contenu',
        'nav': [('/traversee-bateau-espagne-maroc/', 'Venir au Maroc'), ('/que-faire-a-marrakech/', 'Marrakech'),
                ('/#villes', 'Les villes'), ('/#cdm2030', '2030')],
        'other': 'EN', 'crumb_home': 'Accueil', 'updated': 'Mis à jour le', 'published': 'Publié le', 'by': 'Par la rédaction de Morocco Fan Guide',
        'photo': 'Photo', 'photos': 'Crédits photo', 'read': 'min de lecture',
        'f_about': ('Morocco Fan Guide', "Guide indépendant tenu par un passionné de football qui vit au Maroc : des conseils pratiques, vérifiés et mis à jour."),
        'f_links': 'À lire', 'f_info': 'Transparence', 'about': ('/a-propos/', 'À propos'), 'privacy': ('/confidentialite/', 'Confidentialité'),
        'indep': 'Site indépendant, sans lien avec la FIFA, la Fédération royale marocaine de football ni les organisateurs du tournoi.',
        'aff': "Certains liens peuvent être des liens affiliés : si vous réservez par leur intermédiaire, nous pouvons recevoir une commission, sans surcoût pour vous.",
        'cookies': "Les outils de notre partenaire d'affiliation (Travelpayouts) peuvent déposer des cookies pour attribuer les réservations.",
        'months': ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
    },
    'en': {
        'home': '/en/', 'skip': 'Skip to content',
        'nav': [('/en/ferry-spain-morocco/', 'Getting there'), ('/en/things-to-do-in-marrakech/', 'Marrakech'),
                ('/en/#cities', 'Cities'), ('/en/#wc2030', '2030')],
        'other': 'FR', 'crumb_home': 'Home', 'updated': 'Updated', 'published': 'Published', 'by': 'By the Morocco Fan Guide team',
        'photo': 'Photo', 'photos': 'Photo credits', 'read': 'min read',
        'f_about': ('Morocco Fan Guide', 'An independent guide run by a football fan who lives in Morocco: practical, checked and up-to-date advice.'),
        'f_links': 'Read next', 'f_info': 'Transparency', 'about': ('/en/about/', 'About'), 'privacy': ('/en/privacy/', 'Privacy'),
        'indep': 'Independent website, not affiliated with FIFA, the Royal Moroccan Football Federation or the tournament organisers.',
        'aff': 'Some links may be affiliate links: if you book through them, we may earn a commission at no extra cost to you.',
        'cookies': 'Tools from our affiliate partner (Travelpayouts) may set cookies to attribute bookings.',
        'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    },
}
e = html.escape


def fmt_date(d, lang):
    y, m, j = d.split('-')
    mois = T[lang]['months'][int(m) - 1]
    return f'{int(j)} {mois} {y}'


def load():
    pages = []
    for lang in ('fr', 'en'):
        folder = os.path.join(BASE, 'contenu', lang)
        for f in sorted(os.listdir(folder)):
            if not f.endswith('.html'):
                continue
            raw = open(os.path.join(folder, f), encoding='utf-8').read()
            m = re.match(r'\s*<!--meta\s+(\{.*?\})\s*-->\s*', raw, re.S)
            if not m:
                raise SystemExit(f'métadonnées absentes : {lang}/{f}')
            meta = json.loads(m.group(1))
            meta['lang'] = lang
            meta['body'] = raw[m.end():]
            meta.setdefault('image', DEFAULT_IMG.get(meta.get('crumb', ''), 'benhaddou'))
            if meta['image'] not in IMAGES:
                raise SystemExit(f'image inconnue dans outils/images.json : {meta["image"]} ({lang}/{f})')
            pages.append(meta)
    return pages


def img(key, lang, used, cls='', big=False, eager=False):
    """Balise <img> d'une photo de images.json ; enregistre la clé pour les crédits."""
    i = IMAGES[key]
    used.append(key)
    src = i['file'] if big else i['small']
    srcset = f'{i["small"]} 500w, {i["file"]} {i["w"]}w'
    sizes = '(max-width: 1100px) 100vw, 1100px' if big else '(max-width: 640px) 100vw, 360px'
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="{src}" srcset="{srcset}" sizes="{sizes}" width="{i["w"]}" height="{i["h"]}" '
            f'alt="{e(i["alt_" + lang])}" {load} decoding="async">')


def credit(key, lang):
    i = IMAGES[key]
    lic = f'<a href="{i["license_url"]}" rel="license noopener">{e(i["license"])}</a>'
    return f'{T[lang]["photo"]} : <a href="{i["source"]}" rel="noopener">{e(i["author"])}</a>, {lic}, Wikimedia Commons'


def reading_time(body):
    words = len(re.sub('<[^>]+>', ' ', body).split())
    return max(1, round(words / 220))


def faq(body, lang):
    """Données structurées FAQPage tirées de la section id="faq" (questions en h3, réponse au premier paragraphe)."""
    if 'id="faq"' not in body:
        return None
    qs = re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>', body.split('id="faq"', 1)[1], re.S)
    strip = lambda x: html.unescape(re.sub(r'<[^>]+>', '', x)).strip()
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'inLanguage': lang,
            'mainEntity': [{'@type': 'Question', 'name': strip(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}}
                           for q, a in qs]} if qs else None


def by_date(pages):
    return sorted(pages, key=lambda q: (q.get('published', q['updated']), q['path']), reverse=True)


def cards(p, pages, used):
    arts = by_date(q for q in pages if q['lang'] == p['lang'] and q['type'] == 'article')
    out = []
    for q in arts:
        out.append(f'''<article class="post">
  <a class="post-img" href="{q['path']}" tabindex="-1" aria-hidden="true">{img(q['image'], p['lang'], used)}</a>
  <p class="kicker">{e(q.get('crumb', ''))}</p>
  <h3><a href="{q['path']}">{e(q.get('short', q['title']))}</a></h3>
  <p>{e(q['description'])}</p>
  <p class="post-meta">{fmt_date(q['updated'], p['lang'])} · {reading_time(q['body'])} {T[p['lang']]['read']}</p>
</article>''')
    return '<div class="posts">' + '\n'.join(out) + '</div>'


# Version du CSS dans son URL : une page neuve ne s'affiche jamais avec une ancienne feuille de style en cache
CSS_V = hashlib.sha256(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'style.css'), 'rb').read()).hexdigest()[:8]


def render(p, pages):
    t = T[p['lang']]
    lang = p['lang']
    url = DOMAIN + p['path']
    used = []
    fr_path, en_path = (p['path'], p['alt']) if lang == 'fr' else (p['alt'], p['path'])
    nav = ''.join(f'<a href="{h}">{e(l)}</a>' for h, l in t['nav'])
    other_lang = 'en' if lang == 'fr' else 'fr'
    lang_link = f'<a class="lang" href="{p["alt"]}" hreflang="{other_lang}" lang="{other_lang}">{t["other"]}</a>'
    articles = by_date(q for q in pages if q['lang'] == lang and q['type'] == 'article')
    links = ''.join(f'<li><a href="{q["path"]}">{e(q.get("short", q["title"]))}</a></li>' for q in articles)
    body = p['body'].replace('[[articles]]', cards(p, pages, used) if '[[articles]]' in p['body'] else '')
    body = re.sub(r'\[\[img:([a-z0-9-]+)(?:\|([a-z -]+))?\]\]',
                  lambda m: img(m.group(1), lang, used, m.group(2) or '', big='big' in (m.group(2) or ''),
                                eager='eager' in (m.group(2) or '')), body)
    hero = IMAGES[p['image']]
    ld = {'@context': 'https://schema.org', 'inLanguage': lang, 'url': url, 'description': p['description'],
          'image': DOMAIN + hero['file']}
    if p['type'] == 'article':
        ld.update({'@type': 'Article', 'headline': p['title'], 'dateModified': p['updated'],
                   'datePublished': p.get('published', p['updated']),
                   'author': {'@type': 'Organization', 'name': 'Morocco Fan Guide', 'url': DOMAIN + t['about'][0]},
                   'publisher': {'@type': 'Organization', 'name': 'Morocco Fan Guide'}})
        figure = (f'<figure class="lead-img">{img(p["image"], lang, [], big=True, eager=True)}'
                  f'<figcaption>{credit(p["image"], lang)}</figcaption></figure>')
        top = (f'<header class="article-head wrap"><p class="crumbs"><a href="{t["home"]}">{t["crumb_home"]}</a> / '
               f'{e(p.get("crumb", ""))}</p><h1>{re.sub(" ([:;?!])", "\u00a0\\1", e(p["title"]))}</h1>'
               f'<p class="byline">{t["by"]} · {t["published" if p["updated"] == p.get("published") else "updated"]} '
               f'{fmt_date(p["updated"], lang)} · '
               f'{reading_time(p["body"])} {t["read"]}</p></header>'
               f'<div class="wrap wide">{figure}</div>'
               f'<main id="contenu" class="wrap article">{body}</main>')
    elif p['type'] == 'page':
        ld.update({'@type': 'WebPage', 'name': p['title'], 'dateModified': p['updated']})
        top = (f'<header class="article-head wrap"><p class="crumbs"><a href="{t["home"]}">{t["crumb_home"]}</a> / '
               f'{e(p.get("crumb", ""))}</p><h1>{re.sub(" ([:;?!])", "\u00a0\\1", e(p["title"]))}</h1></header>'
               f'<main id="contenu" class="wrap article">{body}</main>')
    else:
        ld.update({'@type': 'WebSite', 'name': 'Morocco Fan Guide'})
        top = f'<main id="contenu">{body}</main>'
    # Crédits des photos de la page qui n'ont pas déjà leur légende (accueil : vignettes, villes)
    seen = []
    for k in used:
        if k not in seen:
            seen.append(k)
    credits = ''
    if seen:
        credits = (f'<div class="wrap photo-credits"><p><strong>{t["photos"]}</strong> — '
                   + ' · '.join(f'{e(IMAGES[k]["alt_" + lang])} : {credit(k, lang).split(" : ", 1)[1]}' for k in seen)
                   + '</p></div>')
    fq = faq(p['body'], lang) if p['type'] == 'article' else None
    faq_ld = f'  <script type="application/ld+json">{json.dumps(fq, ensure_ascii=False)}</script>\n' if fq else ''
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="p:domain_verify" content="b4d51b3210500f942687322ba8b475f9"/>
{DRIVE}  <title>{e(p.get('seo_title', p['title']))}</title>
  <meta name="description" content="{e(p['description'])}">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="fr" href="{DOMAIN}{fr_path}">
  <link rel="alternate" hreflang="en" href="{DOMAIN}{en_path}">
  <link rel="alternate" hreflang="x-default" href="{DOMAIN}{fr_path}">
  <meta property="og:type" content="{'article' if p['type'] == 'article' else 'website'}">
  <meta property="og:title" content="{e(p.get('seo_title', p['title']))}">
  <meta property="og:description" content="{e(p['description'])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{DOMAIN}{hero['file']}">
  <meta property="og:image:width" content="{hero['w']}">
  <meta property="og:image:height" content="{hero['h']}">
  <meta property="og:site_name" content="Morocco Fan Guide">
  <meta property="og:locale" content="{'fr_FR' if lang == 'fr' else 'en_GB'}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#ffffff">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="/fonts/source-serif-4-latin-700.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/style.css?v={CSS_V}">
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{faq_ld}</head>
<body>
  <a class="skip" href="#contenu">{t['skip']}</a>
  <header class="site-header"><div class="wrap">
    <a class="brand" href="{t['home']}"><svg class="logo" width="30" height="30" viewBox="0 0 40 40" aria-hidden="true"><g fill="#a8432a"><rect x="10" y="10" width="20" height="20"/><rect x="10" y="10" width="20" height="20" transform="rotate(45 20 20)"/></g><circle cx="20" cy="20" r="5" fill="#e0b25c"/></svg>Morocco Fan Guide</a>
    {lang_link}
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav"><span class="burger" aria-hidden="true"></span>Menu</button>
    <nav class="nav" id="nav">{nav}</nav>
  </div></header>
  {top}
  {credits}
  <footer class="site-footer">
    <div class="wrap">
      <div><h4>{t['f_about'][0]}</h4><p>{t['f_about'][1]}</p></div>
      <div><h4>{t['f_links']}</h4><ul>{links}</ul></div>
      <div><h4>{t['f_info']}</h4><p>{t['aff']}</p><p>{t['cookies']}</p><p><a href="{t['about'][0]}">{t['about'][1]}</a> · <a href="{t['privacy'][0]}">{t['privacy'][1]}</a></p></div>
    </div>
    <div class="legal"><div class="wrap">{t['indep']}</div></div>
  </footer>
  <script>(function(){{var b=document.querySelector('.menu-btn'),n=document.getElementById('nav');document.documentElement.classList.add('js');b.addEventListener('click',function(){{var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)}})}})();</script>
</body>
</html>
'''


def main():
    pages = load()
    paths = {p['path'] for p in pages}
    for p in pages:
        if p['alt'] not in paths:
            raise SystemExit(f'traduction manquante : {p["path"]} -> {p["alt"]}')
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    shutil.copytree(os.path.join(BASE, 'static'), SITE)
    for p in pages:
        out = os.path.join(SITE, p['path'].strip('/'), 'index.html')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8').write(render(p, pages))
    urls = []
    for p in pages:
        fr_path, en_path = (p['path'], p['alt']) if p['lang'] == 'fr' else (p['alt'], p['path'])
        urls.append(f'''  <url>
    <loc>{DOMAIN}{p['path']}</loc>
    <lastmod>{p['updated']}</lastmod>
    <xhtml:link rel="alternate" hreflang="fr" href="{DOMAIN}{fr_path}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{DOMAIN}{en_path}"/>
  </url>''')
    open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(urls) + '\n</urlset>\n')
    # Flux RSS pour la publication automatique d'épingles Pinterest (un flux par langue, un item par article)
    import email.utils, datetime
    for lang, out in (('fr', 'pinterest.xml'), ('en', 'en/pinterest.xml')):
        items = []
        for q in by_date(q for q in pages if q['lang'] == lang and q['type'] == 'article'):
            i = IMAGES[q['image']]
            size = os.path.getsize(os.path.join(BASE, 'static', i['file'].lstrip('/')))
            pub = datetime.datetime.fromisoformat(q.get('published', q['updated']) + 'T08:00:00+00:00')
            items.append(f'''  <item>
    <title>{e(q.get('seo_title', q['title']))}</title>
    <link>{DOMAIN}{q['path']}</link>
    <guid isPermaLink="true">{DOMAIN}{q['path']}</guid>
    <description>{e(q['description'])}</description>
    <pubDate>{email.utils.format_datetime(pub)}</pubDate>
    <enclosure url="{DOMAIN}{i['file']}" length="{size}" type="image/jpeg"/>
    <media:content url="{DOMAIN}{i['file']}" medium="image" type="image/jpeg" width="{i['w']}" height="{i['h']}"/>
  </item>''')
        home = DOMAIN + T[lang]['home']
        desc = T[lang]['f_about'][1]
        open(os.path.join(SITE, out), 'w', encoding='utf-8').write(
            '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" '
            'xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
            f'  <title>Morocco Fan Guide{"" if lang == "fr" else " (English)"}</title>\n  <link>{home}</link>\n'
            f'  <description>{e(desc)}</description>\n  <language>{"fr-FR" if lang == "fr" else "en-GB"}</language>\n'
            f'  <atom:link href="{DOMAIN}/{out}" rel="self" type="application/rss+xml"/>\n'
            + '\n'.join(items) + '\n</channel>\n</rss>\n')
    print(f'{len(pages)} pages générées')


main()
