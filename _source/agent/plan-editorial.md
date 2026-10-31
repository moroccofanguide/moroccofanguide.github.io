# Plan éditorial — moroccofanguide.com

Règle : au plus 2 nouveaux articles par semaine (lundi et jeudi), en français ET en anglais, choisis en haut de la liste « À écrire », chacun avec du vécu vérifié par outils/sources_vecu.py (voir routine-quotidienne.md, étape 3a).
Priorité = volume de recherche × intention de réservation (activités GetYourGuide, ferry, hôtels) ÷ concurrence.
Volumes : OpenRush, France, octobre 2026 (confiance 0,7). Vérifier chaque fait avant publication.

## Longue traîne (décision d'abdallah, 2026-10-27)
Le site est trop jeune pour les requêtes courtes (« bateau espagne maroc » : pos. 80-90). On vise d'abord les
questions précises de 3 mots et plus, peu disputées : chaque article et chaque mise à jour répond en haut de page,
en 1-2 phrases, aux questions exactes (durée, distance, prix, horaires, sécurité, « avec voiture », « depuis X »),
puis les reprend en FAQ. Titres construits sur la question réelle, pas sur le mot-clé court.
Sources des questions : requêtes Search Console (y compris celles en pos. 50-100), sections « Autres questions »
lues à la main, forums. Jamais de page quasi identique par variante (pages satellites interdites) : une variante
= une section ou une question de FAQ dans la page existante, une nouvelle page seulement pour un vrai sujet distinct.
Pistes relevées dans Search Console le 27/10 :
- Ferry : « traversée espagne maroc en voiture », « prix bateau espagne-maroc avec voiture », « combien d'heures de
  bateau espagne maroc » (section voiture + FAQ faites/à compléter).
- Prix : « combien coûte un café au maroc », « café taxi marrakech » (titre refait le 27/10).
- Sécurité : « place jemaa el-fna dangereux », « marrakech la nuit dangereux » (titre refait le 27/10).
- Agafay : « la dune agafay », « aziz agafay desert » (noms de camps : pas de page dédiée).
Volumes et concurrence (OpenSEO, Google France, 27/10 ; « concurrence » = enchères Google Ads, KD = difficulté SEO 0-100) :
- sete tanger bateau 5 400 (KD 0, conc. moyenne) ; bateau sete tanger 3 600 → article Sète-Tanger prioritaire.
- bateau espagne maroc 1 900 ; ferry espagne maroc 1 000 ; traversée espagne maroc 1 000 (KD 0, conc. moyenne/moyenne/moyenne) ;
  billet bateau espagne maroc 320 ; prix bateau espagne maroc 140 ; durée traversée 70 ; en voiture 50 ; avec voiture (prix) 40.
- bateau tarifa tanger 720 (KD 21, conc. forte).
- taxi maroc 590 ; prix taxi marrakech 480 ; prix taxi maroc 170 (KD 0, conc. faible) → titre taxis recentré le 27/10.
- prix maroc 210 ; prix au maroc 170 ; prix café maroc 20 ; combien coûte un café au maroc 20.
- marrakech la nuit 110 ; place jemaa el fna dangereux 110 ; marrakech la nuit dangereux 20 ; marrakech dangereux 30.
Limite : KD 0 partout sur le ferry alors que la page est en pos. 70-90 : le KD de cette source sous-estime la difficulté en France.
Idées DataForSEO (Google Ads France, 27/10, 5 728 idées, fichier donnees/20261027-201319-idees.json ; conc. = enchères Ads) :
- Aéroport de Marrakech (8 100/mois × plusieurs formulations, conc. faible) : arrivée, taxi (prix), bus, transfert → nouvel article, lien taxis.
- Sète – Tanger (5 400 + 3 600 + gnv sete tanger 2 400 + ferry sete tanger 1 000, conc. moyenne) → article prioritaire confirmé.
- Change euro / dirham (14 800, 12 100, devise du maroc 3 600, taux de change maroc 880, conc. faible) : intention surtout
  « convertisseur » (Google affiche le sien) → article « où et comment changer ses euros au Maroc » (bureaux, frais, distributeurs).
- Marrakech → Essaouira (1 600, moyenne), quad à Marrakech (1 900) et buggy (1 000), cascade d'Ouzoud (590, faible).
- Place Jemaa el-Fna (18 100, faible) et souk de Marrakech (5 400, faible) : pages existantes, titres à vérifier.
Nouveaux articles : préférer « Sète – Tanger en bateau » (question précise, KD 0) à des sujets génériques.

## Publiés
- 2026-10-15 — Bateau pour le Maroc (/traversee-bateau-espagne-maroc/ · /en/ferry-spain-morocco/)
- 2026-10-15 — Excursions depuis Marrakech (/excursions-depuis-marrakech/ · /en/day-trips-from-marrakech/) — « excursion marrakech » 2 900/mois
- 2026-10-16 — Que faire à Marrakech (/que-faire-a-marrakech/ · /en/things-to-do-in-marrakech/) — 4 400/mois
- 2026-10-17 — Désert d'Agafay (/desert-agafay/ · /en/agafay-desert/) — « desert agafay » / « agafay » 8 100/mois chacun
- 2026-10-19 — Souks de Marrakech (/souks-marrakech/ · /en/marrakech-souks/) — « souk marrakech » 5 400/mois
- 2026-10-20 — Place Jemaa el-Fna (/jemaa-el-fna/ · /en/jemaa-el-fna/) — « marrakech jemaa el fna » 6 600/mois
- 2026-10-22 — Jardin Majorelle (/jardin-majorelle/ · /en/majorelle-garden/) — « majorelle marrakech » 6 600/mois
- 2026-10-29 — Quad à Agafay (/quad-agafay-marrakech/ · /en/quad-biking-agafay-marrakech/) — « quad marrakech » 1 900/mois ; recentré sur Agafay et le quad, sans prix ; 2 témoignages (passportandstamps.com 2025-09, poshinprogress.com 2025-12) ; vécu de l'auteur toujours demandé pour la mise à jour

## À écrire (ordre de priorité — revu le 2026-10-16 d'après les SERP Google FR mobile)
Règle de priorité : d'abord les requêtes où de PETITS sites sont en tête (place prenable par un site neuf),
avec intention de réservation ; les requêtes tenues par des opérateurs ou gros comparateurs viennent après.
1. Sète – Tanger en bateau : durée (39-48 h), ports, conseils — « sete tanger » / « sete tanger bateau » 5 400, KD 0
   (opérateurs en tête : viser les questions pratiques). [ancien n° 2, devenu 1 le 2026-10-29 : quad publié]
3. Essaouira : que faire, y aller depuis Marrakech — « essaouira maroc » 9 900, KD 8.
4. Chefchaouen : que faire, comment y aller depuis Tanger ou Fès — « chefchaouen » 40 500, KD 8 (SERP à vérifier).
5. Aéroport de Marrakech-Ménara : rejoindre la ville (taxi, bus, transfert) — « aeroport marrakech » 8 100, KD 0.
6. Coupe du monde 2030 au Maroc : villes, stades — « cdm maroc » 2 900 (sources officielles uniquement).
7. Guides de villes de l'accueil (tuiles « Guide à venir » depuis le 24/10, demande d'abdallah) : Fès, Tanger, Casablanca, Rabat, Agadir — volumes à vérifier, une tuile devient cliquable dès que son guide est publié.
8. Train Al Boraq ; Tanger Med ; assurance voiture ; Merzouga 3 jours ; Opération Marhaba.

## Idées à valider par les données avant d'écrire
- Stades de la Coupe du monde 2030 au Maroc (« stade maroc cdm 2030 » 390/mois)
- Rabat que faire ; Ouzoud ; Imlil ; montgolfière Marrakech ; hammam Marrakech
- Versions anglaises : vérifier les volumes Royaume-Uni/États-Unis (« day trips from marrakech », « ferry to morocco »)
