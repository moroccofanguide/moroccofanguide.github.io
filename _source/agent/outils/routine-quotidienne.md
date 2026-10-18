Routine quotidienne du projet perso moveon (site https://moroccofanguide.com). Tâche planifiée sans écran :
personne ne lit cette session, seul ton rapport final est lu. Réponds en français.
Objectif principal : générer du revenu passif (affiliation Travelpayouts : activités, ferry, hôtels).
Dossier du projet : /srv/agent/workspace/clients/perso/sujets/moveon (fais `cd` dedans avant toute commande).

1. Lis notes.md, plan-editorial.md et les 20 dernières lignes de journal.md.
2. Contrôle SEO technique du site en ligne (curl) :
   - toutes les URL de https://moroccofanguide.com/sitemap.xml répondent 200 avec une page complète (`</html>`),
     et http:// redirige vers https:// ;
   - chaque page a un title (≤ 65 caractères), une meta description (≤ 160), un canonical, la paire hreflang FR/EN ;
   - aucun lien interne cassé ;
   - corrige dans contenu/ ou outils/build.py tout problème trouvé.
   Si notes.md indique que Search Console est connectée, regarde les requêtes et pages qui progressent et améliore-les.
2b. Revenus : lance EXACTEMENT `python3 -I outils/stats.py 7` (lecture seule, n'affiche jamais le jeton). Note dans
   journal.md les clics vers les partenaires (type redirect : popunder = integration_background, liens convertis =
   link_switcher) et les gains. Si une page reçoit des visites mais aucun clic, renforce son encadré « Réserver ».
   Première réservation ou premier gain : signale-le en 🟠 (bonne nouvelle à transmettre à l'utilisateur).
3. Écris UN nouvel article : le premier de « À écrire » dans plan-editorial.md, en français ET en anglais
   (format de contenu/ : commentaire meta JSON puis HTML ; sommaire .toc ; tableau ; FAQ ; mention « indicatif » ;
   title SEO ≤ 65 caractères, description ≤ 145). Prends modèle sur contenu/fr/excursions-depuis-marrakech.html.
   - Vérifie chaque fait (WebSearch : sources officielles ou plusieurs sources concordantes) ; dans le doute, formule
     prudemment ou retire l'information. Jamais de faux avis, de faux prix, de faux liens affiliés.
   - Ajoute des liens internes vers et depuis les articles proches.
   - Revenu : ajoute un encadré `<aside class="book">` (modèle dans contenu/fr/excursions-depuis-marrakech.html) avec
     1 à 3 liens directs vers les partenaires utiles au lecteur (GetYourGuide pour les activités, Booking.com pour
     l'hébergement), rel="sponsored noopener", et la mention « Liens partenaires ». Adresse vérifiée par WebSearch
     (page catégorie ou ville, pas une offre isolée) ; jamais de lien inventé. Le script Travelpayouts Drive les
     convertit en liens affiliés.
   - Photo : mets dans les métadonnées "image": "<clé>" (clés dans outils/images.json, une même photo pour FR et EN).
     Si aucune ne correspond au sujet, cherche-en une libre : `python3 -I outils/photo.py --chercher "<lieu>"`,
     regarde la vignette avant de choisir (paysage, nette, sans texte ni personne au premier plan), puis
     `python3 -I outils/photo.py <clé> "<titre exact>" "<alt FR>" "<alt EN>"`. Si l'outil échoue, ne mets pas
     de clé : le générateur prend une photo par défaut. Jamais d'image hors de cet outil (droits d'auteur).
4. Depuis le dossier du projet (`cd` dans une commande séparée), lance EXACTEMENT, seules et sans `&&`, `;` ni `cd` devant
   (ces formes sont pré-autorisées, toute autre peut être refusée) : `python3 -I outils/build.py`, contrôle du HTML
   généré, `python3 -I outils/synchro.py` (« git pull » : un autre agent publie aussi sur le dépôt GitHub, qui fait
   référence), puis `python3 -I outils/publier.py "<message>"`.
   - Un autre agent publie aussi ; sa source éventuelle est dans le dépôt sous _source/ (la nôtre : _source/agent/,
     envoyée automatiquement par publier.py, voir README.md du projet). Mets aussi à jour static/llms.txt à chaque article.
   - Si synchro.py liste des pages « À RECONSTITUER » : reporte dans contenu/ (métadonnées et corps) ce qui a changé
     dans la page en ligne, sans rien perdre de son contenu, relance build.py puis synchro.py jusqu'au code retour 0.
     Aucune ligne « PERTE » ne doit rester. Si les seuls écarts restants sont volontaires (ordre, temps de lecture),
     note-le dans le rapport en 🟠 : l'utilisateur ou une session interactive lancera `synchro.py --accepter`.
     S'il a téléchargé des fichiers dans static/, relance build.py puis synchro.py.
   - Ne publie jamais tant que synchro.py ne répond pas OK : publier.py refuse de toute façon, et ne supprime jamais
     rien dans le dépôt. Si tu n'arrives pas à reconstituer une page, ne publie pas et signale-le en 🟠.
   Fais la synchro aussi au début de la routine (après l'étape 1), pour écrire l'article sur une base à jour.
   vérifie que les nouvelles pages répondent 200 en ligne avec `</html>` (attends le déploiement GitHub Pages,
   jusqu'à 5 minutes).
5. Mets à jour plan-editorial.md (article déplacé dans « Publiés ») et ajoute une ligne datée dans journal.md
   (publié, corrigé, constaté).
6. Interdits : afficher un secret (jeton GitHub, sujet ntfy), contacter un serveur, installer quoi que ce soit,
   créer ou modifier une tâche planifiée, toucher à un autre dossier que celui du projet.
   Si une action est refusée ou une étape échoue : ne la contourne pas, note-la dans le rapport et continue
   ce qui ne dépend pas d'elle.

Termine OBLIGATOIREMENT ta réponse par ce bloc (c'est lui qui déclenche la notification ntfy de l'utilisateur) :

## Résumé
- 🟢 OK : <ce qui a été publié et vérifié, avec les URL>
- 🟠 À surveiller : <action utile de l'utilisateur : accès expiré (le jeton GitHub expire 90 jours après le
  2026-10-15), décision, achat, compte à son nom>
- 🔴 Problème : <publication échouée ou site cassé>

Les lignes 🟠 et 🔴 n'existent QUE s'il y a quelque chose à y mettre : sinon, ne les écris pas du tout et n'utilise
ces deux symboles nulle part ailleurs dans ta réponse (leur seule présence envoie une notification à l'utilisateur).
