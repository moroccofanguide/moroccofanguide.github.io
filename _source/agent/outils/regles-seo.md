# Règles SEO globales (copie des instructions communes à tous les agents)

Source : instructions globales d'Abdallah, version du 2026-10-21. Pour ce projet, l'outil de sources est outils/sources_vecu.py et le fichier d'état du contrôle mensuel est outils/etat-guides-google.json.

SEO BASELINE (applies to every agent, every site, every SEO task)

References (English versions are authoritative, translations lag behind):
[A] SEO Starter Guide
    https://developers.google.com/search/docs/fundamentals/seo-starter-guide?hl=en
[B] Spam policies for Google web search
    https://developers.google.com/search/docs/essentials/spam-policies?hl=en
[C] Guidance on using generative AI content
    https://developers.google.com/search/docs/fundamentals/using-gen-ai-content?hl=en
Always follow all three. If a task conflicts with any of them, do not proceed: flag it to me.

RULES [A] SEO STARTER GUIDE (version "Last updated 2025-12-10")

Discovery and indexing
- Check indexing with site:domain and Search Console URL Inspection, not by guessing.
- Google finds pages mainly through links: every new page gets internal links from relevant existing pages. Sitemap is kept up to date but is secondary.
- Google must see what a browser sees: never block CSS, JS or images in robots.txt.
- To keep a page out of Google, use the supported methods (noindex, robots.txt for crawling), never tricks.

Site structure
- Descriptive URLs made of words useful to users, no random IDs.
- One URL per piece of content: redirect non-preferred URLs (301), use rel="canonical" when a redirect is impossible.
- Do not reorganize an existing structure only for SEO.

Content
- Clear, correct writing, split into paragraphs and headed sections.
- Original content only: never copy or rehash other sites.
- Keep content current: update or remove outdated pages.
- People-first, helpful, reliable: cite expert or official sources.
- Cover the different ways people phrase the same need (local and international wording).
- No ads or interstitials that block or disrupt reading.
- Link to relevant internal pages and trustworthy external sources, with descriptive anchor text (never "click here").
- Add nofollow (or rel="ugc"/"sponsored") to untrusted, user-generated and affiliate links.

Search appearance
- Every page: a unique, clear, concise <title> that matches the content.
- Every page: a short, unique meta description covering the most relevant points.
- Images: sharp and relevant, placed near related text, with descriptive alt text.
- Videos: on a standalone page near relevant text, with a descriptive title and description.

Promotion
- Social media, communities, word of mouth: yes, but never excessive (see my platform rules: own accounts only, no automated group posting, no automated link building).

Do NOT spend effort on (Google says these do not matter or are harmful)
- meta keywords tag (ignored by Google)
- keyword stuffing (spam)
- keywords in domain name or URL path for ranking
- target word counts (no minimum or maximum length)
- subdomain vs subdirectory debates
- heading count or order for ranking
- chasing PageRank alone
- treating E-E-A-T as a ranking factor (it is not one; write helpful content instead)

RULES [B] SPAM POLICIES (version "Last updated 2026-08-28")
Never do, never let happen:
- Cloaking: same content for Google and for visitors.
- Doorway pages: no near-duplicate pages per city/keyword funnelling to one destination.
- Hidden text or links, keyword stuffing.
- Link spam: no bought, exchanged or automated links. Every affiliate, paid or sponsored link carries rel="sponsored" (or rel="nofollow").
- Scaled content abuse: no mass-produced pages with little value, whatever the tool.
- Scraping: no republishing or light rewriting of other sites' content.
- Thin affiliation: affiliate pages must add original value (local experience, comparisons, real prices), never copied merchant descriptions.
- Sneaky redirects, back button hijacking, misleading functionality (every tool we advertise must work).
- Site reputation abuse: no third-party content hosted to exploit our sites' ranking.
- Machine-generated traffic: never send automated queries to Google (no rank-tracking scrapers). Use Search Console and its API instead.
- Security: keep sites free of hacked content, malware, unwanted software. Watch for injected pages or scripts in the weekly check.
- Policy circumvention: never move a penalised practice to a subdomain or new site.

RULES [C] GENERATIVE AI CONTENT (version "Last updated 2026-10-01")
- AI is allowed for research and structure; every page must add value for users.
- Manually fact-check every AI-assisted text before publishing (models predict words, they do not retrieve facts). List the sources used.
- Same review for metadata: title, meta description, structured data, image alt text.
- Structured data must follow Google's general and feature-specific guidelines and be validated.
- Give readers context on how content was made when relevant (for example an "about" or "how we test" note).
- AI-generated images: add image metadata (IPTC DigitalSourceType = TrainedAlgorithmicMedia).
- Use the Search Quality Rater Guidelines sections 4.6.5 and 4.6.6 as the quality bar: no low-effort, unoriginal main content.

LIVED-EXPERIENCE SOURCES (mandatory for every content task: new article or update)
Goal: every page carries real experience, not a rewrite of what everyone else says (rules [B] scaled content, [C] 4.6.6).
1. Author input first: read the author's notes for this page (MFG: contenu/vecu/<slug>.md). Use them faithfully, never embellish.
2. Then traveller and user testimonies, found with the sources tool and WebSearch, read with WebFetch:
   forums (Voyageforum, Routard, TripAdvisor forums, specialist forums), Reddit, YouTube vlogs and comments,
   Q&A sites, public social media posts. For technical sites: Stack Exchange, Reddit sysadmin subs, provider community forums.
3. Record every source used with the sources tool (one ledger per page: type, URL, month, summary).
4. Minimum to publish: the author's input, OR at least 2 concordant testimonies from 2 different sites, less than 36 months old.
   Otherwise: write a draft, do not publish, ask me 3 precise questions about my own experience.
5. How to use testimonies:
   - summarise in your own words; quotes of 25 words maximum, with a link to the source;
   - present them as testimonies ("travellers report on ..."), never as the author's own experience;
   - no usernames, names, emails or phone numbers;
   - never use content behind a login (private Facebook groups, closed communities) or copy reviews in bulk
     (Google Maps, TripAdvisor, Booking): that is scraping under [B] and breaks those sites' terms;
   - a testimony is not a fact: prices, rules, opening hours and safety advice are confirmed with official
     or multiple recent sources, otherwise written cautiously or left out;
   - prefer the most recent testimonies and say when a price or situation was reported.
6. Tools: MFG agent uses outils/sources_vecu.py. Other agents use the "lived-experience-sources" skill (same commands).

MONTHLY UPDATE CHECK (on the 1st of each month, for [A], [B] and [C])
1. Fetch each English page above.
2. Read its "Last updated" date (bottom of the page, format YYYY-MM-DD UTC).
3. Compare with the dates stored in the state file (kept inside the agent's own project folder, for example state/google-guidelines.json, one entry per page: {"url": "...", "last_updated": "2025-12-10", "checked": "<date>", "sha256": "<hash of normalized main text>"}).
   Initial values: [A] 2025-12-10, [B] 2026-08-28, [C] 2026-10-01.
   Also compare the SHA-256 of the main article text (navigation, cookie banner and footer removed), because small edits do not always change the date.
4. If nothing changed: update "checked" and stop. No message needed.
5. If something changed:
   - save the new text next to the old one and produce a diff;
   - send me a short summary: what changed, which rules above are affected, proposed new wording;
   - wait for my OK before changing these instructions in any agent;
   - after my OK, update the matching RULES section, its version date and the state file.
6. If the page cannot be fetched or its structure changed (no "Last updated" found), alert me instead of failing silently.
