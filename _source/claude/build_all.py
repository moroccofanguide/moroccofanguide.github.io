import json, re, sys, os, html

ROOT = sys.argv[1]
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")
DATE = "2026-10-17"
SITE = "https://moroccofanguide.com"

IMG = {
 "jemaa": dict(w=960, h=522, src="jemaa", file="Jamaa_El_Fna,_Marrakesh,_Morocco,_20250124_1804_7017.jpg", author="Jakub Hałun", lic="https://creativecommons.org/licenses/by/4.0", licname="CC BY 4.0",
               alt_fr="La place Jemaa el-Fna à Marrakech en fin de journée", alt_en="Jemaa el-Fna square in Marrakech in the late afternoon"),
 "rabat": dict(w=960, h=718, src="rabat", file="Hassan_Tower_01.jpg", author="Bernard Gagnon", lic="https://creativecommons.org/licenses/by-sa/3.0", licname="CC BY-SA 3.0",
               alt_fr="La tour Hassan et ses colonnes à Rabat", alt_en="Hassan Tower and its columns in Rabat"),
 "agadir": dict(w=960, h=720, src="agadir", file="Plage_d%27Agadir_-_from_Dunes_d%27Or_Hotel_2.jpg", author="Ideophagous", lic="https://creativecommons.org/publicdomain/zero/1.0/deed.en", licname="CC0",
               alt_fr="La plage d'Agadir au coucher du soleil", alt_en="Agadir beach at sunset"),
 "tanger": dict(w=960, h=708, src="tanger", file="Photo_du_Port_de_Tanger_Ville_072.jpg", author="Jobt1962", lic="https://creativecommons.org/licenses/by-sa/4.0", licname="CC BY-SA 4.0",
               alt_fr="Vue aérienne du port de Tanger Ville et de la baie", alt_en="Aerial view of Tangier city port and bay"),
}

# (fr_slug, en_slug) pairs
PAIRS = {
 "night": ("/marrakech-la-nuit-securite/", "/en/is-marrakech-safe-at-night/"),
 "safe": ("/maroc-pays-sur/", "/en/is-morocco-safe/"),
 "taxi": ("/taxis-maroc/", "/en/taxis-in-morocco/"),
 "prix": ("/prix-maroc/", "/en/morocco-prices/"),
}

ART = [
 # order = oldest first; cards are prepended, so the last one ends up on top
 dict(key="night", lang="fr", img="jemaa", body="night_fr.html", minutes=7,
      title="Marrakech la nuit : est-ce dangereux ? Les conseils d'un local",
      desc="Marrakech la nuit est-elle sûre ? Où sortir, arnaques de Jemaa el-Fna, rentrer au riad, conseils aux femmes seules, par un habitant du Maroc.",
      h1="Se promener à Marrakech la nuit : est-ce sûr ? Le point de vue d'un local",
      section="Marrakech", card="Marrakech la nuit : est-ce sûr ?"),
 dict(key="night", lang="en", img="jemaa", body="night_en.html", minutes=7,
      title="Is Marrakech Safe at Night? A Local's Honest Guide",
      desc="Is it safe to walk in Marrakech at night? Where to go, Jemaa el-Fna scams, getting back to your riad and tips for women travelling alone, from a local.",
      h1="Is it safe to walk in Marrakech at night? A local's honest answer",
      section="Marrakech", card="Is Marrakech safe at night?"),
 dict(key="taxi", lang="fr", img="tanger", body="taxi_fr.html", minutes=5,
      title="Taxis au Maroc : petits taxis, grands taxis et VTC",
      desc="Taxis au Maroc : la règle du compteur, éviter le prix touriste, grands taxis à prix fixe et ce qu'il faut savoir sur inDrive, par un habitant du Maroc.",
      h1="Taxis au Maroc : petits taxis, grands taxis et applis VTC, le mode d'emploi",
      section="Se déplacer", card="Taxis au Maroc : le mode d'emploi"),
 dict(key="taxi", lang="en", img="tanger", body="taxi_en.html", minutes=5,
      title="Taxis in Morocco: Petit Taxis, Grands Taxis and Apps",
      desc="Taxis in Morocco: the meter rule, avoiding the tourist price, fixed-price grands taxis and what to know about inDrive, from someone who lives in Morocco.",
      h1="Taxis in Morocco: petit taxis, grands taxis and ride-hailing apps explained",
      section="Getting around", card="Taxis in Morocco explained"),
 dict(key="safe", lang="fr", img="rabat", body="safe_fr.html", minutes=6,
      title="Le Maroc est-il un pays sûr ? Ce qu'un local vous conseille",
      desc="Le Maroc est-il sûr pour les touristes ? Vrais risques, prix touriste, circulation, comment réclamer et numéros d'urgence, par un habitant du Maroc.",
      h1="Le Maroc est-il un pays sûr pour les touristes ? Ce qu'il faut vraiment savoir",
      section="Conseils pratiques", card="Le Maroc est-il un pays sûr ?"),
 dict(key="safe", lang="en", img="rabat", body="safe_en.html", minutes=6,
      title="Is Morocco Safe for Tourists? A Local's Advice",
      desc="Is Morocco safe for tourists? The real risks, the tourist-price trap, traffic, how to complain and emergency numbers, from someone who lives in Morocco.",
      h1="Is Morocco safe for tourists? What you really need to know",
      section="Travel tips", card="Is Morocco safe?"),
 dict(key="prix", lang="fr", img="agadir", body="prix_fr.html", minutes=4,
      title="Prix au Maroc : thé, café, taxi, petit-déjeuner, les repères d'un local",
      desc="Combien coûtent un thé, un café, un petit-déjeuner ou un taxi au Maroc ? Les prix locaux réels pour ne pas payer le prix touriste, par un habitant.",
      h1="Prix au Maroc : combien coûtent thé, café, petit-déjeuner et taxi ?",
      section="Conseils pratiques", card="Prix au Maroc : les repères d'un local"),
 dict(key="prix", lang="en", img="agadir", body="prix_en.html", minutes=4,
      title="Prices in Morocco: Tea, Coffee, Taxis and Breakfast",
      desc="How much do tea, coffee, breakfast and taxis cost in Morocco? Real local prices so you don't pay the tourist price, from someone who lives there.",
      h1="Prices in Morocco: what tea, coffee, breakfast and taxis really cost",
      section="Travel tips", card="Prices in Morocco: a local's benchmarks"),
]

MONTH = {"fr": "17 octobre 2026", "en": "17 October 2026"}

def esc(s): return html.escape(s, quote=True)

def faq_from_body(body):
    part = body.split('id="faq"', 1)[1]
    qs = re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>', part, re.S)
    strip = lambda s: html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
    return [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qs]

def slugs(a):
    fr, en = PAIRS[a["key"]]
    return (fr, en) if a["lang"] == "fr" else (en, fr)

for a in ART:
    lang = a["lang"]; im = IMG[a["img"]]
    slug, alt_slug = slugs(a)
    fr_slug, en_slug = PAIRS[a["key"]]
    template = "desert-agafay/index.html" if lang == "fr" else "en/agafay-desert/index.html"
    src = open(os.path.join(ROOT, template), encoding="utf-8").read()
    assert 'name="p:domain_verify"' in src, "balise Pinterest absente du gabarit"
    body = open(os.path.join(HERE, a["body"]), encoding="utf-8").read().strip()
    url = SITE + slug
    t, d = esc(a["title"]), esc(a["desc"])
    imgurl = f"{SITE}/img/{im['src']}.jpg"
    head_new = (
        f'  <title>{t}</title>\n  <meta name="description" content="{d}">\n'
        f'  <link rel="canonical" href="{url}">\n'
        f'  <link rel="alternate" hreflang="fr" href="{SITE}{fr_slug}">\n'
        f'  <link rel="alternate" hreflang="en" href="{SITE}{en_slug}">\n'
        f'  <link rel="alternate" hreflang="x-default" href="{SITE}{fr_slug}">\n'
        f'  <meta property="og:type" content="article">\n  <meta property="og:title" content="{t}">\n'
        f'  <meta property="og:description" content="{d}">\n  <meta property="og:url" content="{url}">\n'
        f'  <meta property="og:image" content="{imgurl}">\n'
        f'  <meta property="og:image:width" content="{im["w"]}">\n  <meta property="og:image:height" content="{im["h"]}">\n')
    src, n = re.subn(r'  <title>.*?<meta property="og:image:height" content="\d+">\n', lambda m: head_new, src, count=1, flags=re.S); assert n == 1
    article = {"@context": "https://schema.org", "inLanguage": lang, "url": url, "description": a["desc"], "image": imgurl,
               "@type": "Article", "headline": a["h1"], "dateModified": DATE, "datePublished": DATE,
               "author": {"@type": "Organization", "name": "Morocco Fan Guide", "url": f"{SITE}/"},
               "publisher": {"@type": "Organization", "name": "Morocco Fan Guide"}}
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": lang, "mainEntity": faq_from_body(body)}
    ld = ('<script type="application/ld+json">' + json.dumps(article, ensure_ascii=False) + '</script>\n'
          '  <script type="application/ld+json">' + json.dumps(faq, ensure_ascii=False) + '</script>')
    src, n = re.subn(r'<script type="application/ld\+json">.*?</script>', lambda m: ld, src, count=1, flags=re.S); assert n == 1
    old_lang = '<a class="lang" href="/en/agafay-desert/"' if lang == "fr" else '<a class="lang" href="/desert-agafay/"'
    assert old_lang in src
    src = src.replace(old_lang, f'<a class="lang" href="{alt_slug}"')
    alt = im["alt_" + lang]
    photo = "Photo"
    fig = (f'<figure class="lead-img"><img src="/img/{im["src"]}.jpg" srcset="/img/{im["src"]}-500.jpg 500w, /img/{im["src"]}.jpg 960w" '
           f'sizes="(max-width: 1100px) 100vw, 1100px" width="{im["w"]}" height="{im["h"]}" alt="{esc(alt)}" fetchpriority="high" decoding="async">'
           f'<figcaption>{photo} : <a href="https://commons.wikimedia.org/wiki/File:{im["file"]}" rel="noopener">{im["author"]}</a>, '
           f'<a href="{im["lic"]}" rel="license noopener">{im["licname"]}</a>, Wikimedia Commons</figcaption></figure>')
    if lang == "en":
        fig = fig.replace("<figcaption>Photo : ", "<figcaption>Photo: ")
    home = '<a href="/">Accueil</a>' if lang == "fr" else '<a href="/en/">Home</a>'
    byline = (f'Par la rédaction de Morocco Fan Guide · Publié le {MONTH["fr"]} · {a["minutes"]} min de lecture' if lang == "fr"
              else f'By the Morocco Fan Guide team · Published {MONTH["en"]} · {a["minutes"]} min read')
    middle = (f'<header class="article-head wrap"><p class="crumbs">{home} / {esc(a["section"])}</p><h1>{esc(a["h1"])}</h1>'
              f'<p class="byline">{byline}</p></header><div class="wrap wide">{fig}</div>'
              f'<main id="contenu" class="wrap article">{body}\n</main>')
    src, n = re.subn(r'<header class="article-head wrap">.*?</main>', lambda m: middle, src, count=1, flags=re.S); assert n == 1
    out = os.path.join(ROOT, slug.strip("/"), "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(src)
    print("wrote", slug, len(faq["mainEntity"]), "FAQ")

# footers: one link per article in its language (idempotent, refresh label)
for dirpath, _, files in os.walk(ROOT):
    if "/.git" in dirpath: continue
    for f in files:
        if not f.endswith(".html") or f == "404.html": continue
        path = os.path.join(dirpath, f)
        s = open(path, encoding="utf-8").read()
        is_en = '<html lang="en">' in s
        label = "<h4>Read next</h4><ul>" if is_en else "<h4>À lire</h4><ul>"
        if label not in s: continue
        for a in ART:
            if (a["lang"] == "en") != is_en: continue
            slug = slugs(a)[0]
            s = re.sub(r'<li><a href="' + re.escape(slug) + r'">[^<]*</a></li>', '', s)
            s = s.replace(label, label + f'<li><a href="{slug}">{esc(a["card"])}</a></li>', 1)
        open(path, "w", encoding="utf-8").write(s)

# homepage cards: remove existing cards for these slugs, then prepend in order
for lang, home in (("fr", "index.html"), ("en", "en/index.html")):
    path = os.path.join(ROOT, home)
    s = open(path, encoding="utf-8").read()
    for a in ART:
        if a["lang"] != lang: continue
        slug = slugs(a)[0]; im = IMG[a["img"]]
        s = re.sub(r'<article class="post">\s*<a class="post-img" href="' + re.escape(slug) + r'".*?</article>\n?', '', s, flags=re.S)
        meta = f'{MONTH[lang]} · {a["minutes"]} ' + ("min de lecture" if lang == "fr" else "min read")
        card = (f'<article class="post">\n'
                f'  <a class="post-img" href="{slug}" tabindex="-1" aria-hidden="true"><img src="/img/{im["src"]}-500.jpg" srcset="/img/{im["src"]}-500.jpg 500w, /img/{im["src"]}.jpg 960w" sizes="(max-width: 640px) 100vw, 360px" width="{im["w"]}" height="{im["h"]}" alt="{esc(im["alt_" + lang])}" loading="lazy" decoding="async"></a>\n'
                f'  <p class="kicker">{esc(a["section"])}</p>\n'
                f'  <h3><a href="{slug}">{esc(a["card"])}</a></h3>\n'
                f'  <p>{esc(a["desc"])}</p>\n'
                f'  <p class="post-meta">{meta}</p>\n'
                f'</article>\n')
        assert '<div class="posts">' in s
        s = s.replace('<div class="posts">', '<div class="posts">' + card, 1)
    open(path, "w", encoding="utf-8").write(s)

# sitemap
sm = os.path.join(ROOT, "sitemap.xml")
s = open(sm, encoding="utf-8").read()
for key, (fr, en) in PAIRS.items():
    for slug in (fr, en):
        s = re.sub(r'  <url>\n    <loc>' + re.escape(SITE + slug) + r'</loc>.*?</url>\n', '', s, flags=re.S)
        s = s.replace("</urlset>", f'  <url>\n    <loc>{SITE}{slug}</loc>\n    <lastmod>{DATE}</lastmod>\n'
                      f'    <xhtml:link rel="alternate" hreflang="fr" href="{SITE}{fr}"/>\n'
                      f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/>\n  </url>\n</urlset>')
open(sm, "w", encoding="utf-8").write(s)
print("done")
