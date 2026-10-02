# 🚀 PROJETS FUTURS — BlackBox Labs

> Dossier vivant de réflexion stratégique long terme. Ne pas confondre avec la
> feuille de route immédiate (lancement des 12 robots, checkpoints J+30/60/90 —
> voir `README_TRACKING.md` et `CHANCES_DE_RENTABILITE.md`).
>
> Objectif de ce fichier : capturer les pistes d'évolution du produit à moyen/
> long terme, au fur et à mesure qu'elles émergent en discussion, pour ne rien
> perdre et pouvoir les reprendre au bon moment — une fois que BlackBox Labs
> aura été réellement lancé et aura du recul terrain (premiers clients, vrai
> volume, vrais retours).
>
> ⚠️ Ce fichier est enrichi manuellement au fil des discussions. Il n'y a pas
> de veille de marché automatique en tâche de fond — l'utilisateur apporte le
> signal (articles lus, concurrents repérés, idées), qui est ensuite structuré
> et challengé ici.

---

## 📌 Statut actuel (contexte au moment de la rédaction)

- BlackBox Labs (12 robots, 3 catégories) est construit et déployé, mais
  **n'a pas encore eu de vrai lancement public / premiers clients réels**.
- Paddle est encore en mode sandbox (domaine live en attente d'approbation).

> **✅ DÉCISION ACTÉE (01/10)** — Steve clôt la phase de réflexion ouverte
> plus bas dans ce fichier. Conclusion retenue, qui devient la feuille de
> route active :
> 1. **Finir la boucle BlackBox Labs entièrement** — bascule Paddle en
>    production, circuit d'achat complet et fonctionnel — puis le laisser
>    tourner en autonome (revenu passif secondaire, plus d'investissement de
>    temps en croissance/distribution active).
> 2. **Utiliser BlackBox comme socle technique** (boilerplate
>    `00_MASTERBOILERPLATE_V6`, patterns d'intégration API/webhook,
>    expérience Paddle déjà acquise) pour lancer le projet suivant : une
>    offre d'automatisation IA pour PME, avec le **médical/dentaire comme
>    premier domaine d'application** (cabinets dentaires/médicaux —
>    réduction des rendez-vous manqués/no-show).
> 3. **Concevoir ce premier produit médical pour qu'il soit reproductible**
>    dans d'autres secteurs PME par la suite (artisans du bâtiment en
>    second temps, puis au-delà) — un moteur générique + une configuration
>    par vertical, plutôt qu'un outil jetable à usage unique.
>
> ⚠️ **Mise à jour (01/10, soirée)** : l'angle précis "rappels automatiques
> anti no-show" pour le médical/dentaire présente un risque concurrentiel
> majeur — Doctolib Pro (acteur dominant, "centaines de milliers de
> soignants" en France) inclut très probablement déjà cette fonctionnalité
> dans son abonnement tout compris. **Avant toute construction**, valider
> sur le terrain (3-5 appels à des cabinets locaux) si c'est bien le cas.
> Si oui : soit changer d'angle dans le médical (recall de contrôle annuel,
> gestion d'avis Google — moins susceptibles d'être déjà couverts), soit
> redonner la priorité aux artisans du bâtiment. Détail complet dans
> l'entrée du journal datée "01/10, plus tard dans la soirée" plus bas.
>
> Le reste de ce fichier (constat de marché, pistes explorées, journal
> chronologique daté) documente le raisonnement qui a mené à cette décision
> — gardé pour mémoire, pas pour relancer le débat à chaque session.

- Priorité absolue actuelle : terminer la bascule Paddle, puis démarrer le
  premier chantier concret de l'automatisation médicale (démo technique +
  démarchage de cabinets locaux — détail dans le journal daté 01/10).

---

## 🎯 Constat de marché qui a lancé cette réflexion

Le marché des API utilitaires indépendantes (le créneau actuel de BlackBox
Labs) génère généralement peu de revenus (souvent plafonné autour de
quelques centaines d'euros/mois pour les meilleurs acteurs indé), malgré un
boom mondial du nombre de développeurs. Explication retenue :

- Les fonctions vendues (masquage d'email, dédup CSV, normalisation de
  téléphone, etc.) sont **des commodités triviales à recoder soi-même**,
  et l'essor des IA de code (Copilot, ChatGPT) réduit encore l'intérêt de
  payer pour ça — un dev les recrée en 5 minutes avec une IA.
- Marché saturé de clones interchangeables (RapidAPI & co), nivellement
  des prix par le bas, aucune différenciation réelle.
- ➡️ Le boom du dev n'aide donc pas ce créneau : il l'affaiblit, car il
  rend le "faire soi-même" encore plus rapide et accessible.

**Conclusion** : pour construire quelque chose de plus gros que BlackBox
Labs actuel, il faut sortir de la catégorie "wrapper de fonction triviale"
et apporter une valeur qu'un dev seul + une IA ne peuvent PAS recréer
facilement.

---

## 💡 Piste retenue : combiner la puissance du réseau + de l'IA

Ligne directrice explicite de l'utilisateur : **"utilisation de la
puissance des réseaux et de l'IA combinés"**.

### Pourquoi cette combinaison est défendable

- **L'IA seule** est reproductible par n'importe qui (un dev peut demander
  la même chose à ChatGPT).
- **Les données seules** sont déjà captées par les gros acteurs (Cloudflare,
  Akamai...).
- **La combinaison à l'échelle d'un petit fournisseur spécialisé** est rare :
  ça demande à la fois du volume de clients réels ET une couche
  d'intelligence appliquée dessus. C'est un vrai fossé défensif — un dev
  seul ne voit que son propre trafic ; un réseau agrégé voit des patterns
  invisibles à l'échelle individuelle (ex : une IP qui attaque plusieurs
  clients BlackBox le même jour).

### Ce qui rend un outil "indispensable" après un seul essai (à viser)

Trois leviers identifiés, qui se combinent bien avec le réseau+IA :
1. **Révéler un angle mort** — montrer au dev un problème qu'il ne savait
   pas avoir (ex : Sentry pour les erreurs).
2. **Supprimer une angoisse récurrente** — sécurité, monitoring, alerte :
   une fois vue, l'absence devient anxiogène.
3. **Devenir un réflexe ambiant/continu** — pas un appel ponctuel, mais un
   système qui veille en permanence et alerte avant que le problème ne
   devienne visible pour le client lui-même (le vrai "aha moment").

➡️ Direction produit qui en découle : passer de **"API qu'on appelle
ponctuellement"** à **"système qui surveille en continu et alerte"**.

---

## 🔍 Besoins à haut volume identifiés (candidats de segment)

Besoins **créés ou amplifiés par l'explosion de l'IA elle-même** (donc
marché jeune, moins saturé que les API utilitaires classiques) :

1. **Spam/fraude générée par l'IA** (faux comptes, bots de formulaires,
   fraude paiement automatisée, avis/commentaires générés en masse).
   → ⭐ Piste retenue en priorité — la plus proche de l'existant
   (catégorie "Security & Link Integrity" déjà présente dans BlackBox
   Labs) et la plus facile à amorcer avec la base de clients dev actuelle.
2. **Vérification d'identité / anti-fraude sur paiements et créations de
   compte**, en particulier pour le no-code/low-code (Bubble, Webflow,
   Shopify) — volume énorme, besoin permanent.
3. **Modération de contenu généré par IA** (deepfakes, texte halluciné,
   voix synthétique) — besoin en pleine explosion, encore peu de
   fournisseurs matures.
4. **Monitoring de conformité réglementaire IA en temps réel** (RGPD,
   AI Act européen) — marché naissant, opportunité d'être précoce mais
   encore incertain/à surveiller.

---

## 🏹 Segment prioritaire proposé : anti-fraude/anti-bot IA pour indie hackers & micro-SaaS

### Pourquoi ce segment et pas un autre

- **Ne pas affronter frontalement les géants** (Cloudflare Bot Management,
  DataDome, Arkose Labs, Akamai) qui dominent le marché entreprise avec
  des contrats à 5 chiffres/mois et des intégrations lourdes.
- **Viser le segment qu'ils négligent ou survendent** : indie hackers,
  petites agences, micro-SaaS — public déjà connu de BlackBox Labs.
- **Un sous-problème précis plutôt que "anti-fraude" en général** — par
  exemple : uniquement la détection de faux comptes/bots sur formulaires
  d'inscription, sans viser la fraude carte bancaire ni les deepfakes
  vidéo au départ.

### Concept produit esquissé

- Passer d'un `bot_detector` statique ("est-ce que cette requête isolée
  ressemble à un bot ?") à une couche de **réputation vivante partagée** :
  "est-ce que ce comportement, vu sur l'ensemble du réseau BlackBox,
  ressemble à une attaque en cours (vue ailleurs aussi) ?"
- Chaque client alimente (de façon anonymisée, métadonnées comportementales
  uniquement — jamais le contenu des requêtes) un pool de signal commun.
- Une couche IA détecte les patterns émergents à travers tous les clients
  (ex : une IP qui scanne plusieurs sites BlackBox le même jour, un pattern
  de credential-stuffing apparaissant simultanément chez plusieurs clients).
- Le client reçoit une alerte/score de risque **avant** que ça devienne un
  problème visible chez lui.

### Obstacles identifiés à ne pas sous-estimer

1. **Problème de l'œuf et la poule** : ce type de produit n'a de valeur
   qu'avec du volume. À faible nombre de clients, quasiment aucun signal
   utile.
   → Piste de mitigation : combiner le signal propre (même faible) avec
   des flux de menaces publics déjà existants (listes d'IP malveillantes
   connues, bases de bots open-source type Project Honeypot) pour être
   utile dès le premier client, en attendant le volume propre.
2. **Confidentialité** : l'agrégation de signal entre clients doit rester
   strictement sur des métadonnées comportementales, jamais le contenu réel
   des requêtes — sous peine d'entrer en contradiction avec la Privacy
   Policy actuelle de BlackBox Labs (`public/privacy.html`).
3. **Expertise technique requise** (ML, sécurité, qualité des données
   d'entraînement) — chantier de plusieurs mois pour un système solide,
   pas un weekend de code. Ne pas sous-estimer le temps de construction
   d'un vrai système fiable, par opposition à un gadget de façade.

---

## 🗺️ Ordre de marche suggéré (à ne pas lancer avant le bon moment)

1. **Ne rien construire maintenant.** Priorité 100% au lancement réel de
   BlackBox Labs actuel (bascule Paddle live, premiers vrais clients).
2. Une fois un socle de clients réels obtenu : valider l'appétence pour ce
   nouveau besoin en interrogeant directement les clients existants (pas
   en supposant) — voir si le point de douleur "faux comptes/bots" revient
   spontanément.
3. Si validé : prototyper la version "signal public + petite couche IA"
   sur le segment le plus étroit possible (ex : uniquement les formulaires
   d'inscription, un seul cas d'usage) avant d'élargir.
4. Élargir progressivement le périmètre (autres types de fraude, autres
   segments) uniquement une fois le premier cas d'usage éprouvé et rentable.

---

## 📝 Idées en vrac non encore développées

_(section à compléter au fil des discussions futures — nouvelles idées,
articles lus, concurrents repérés, retours clients...)_

- (27/09) **Sites d'affiliation "un moteur, plusieurs niches" (hors Amazon)**

  **Origine** : Steve a suivi la formation d'Olivier Allain (revente Amazon),
  qui recommande Helium10 + SEMrush pour trouver des niches produit et
  Affilae pour l'affiliation. Idée initiale : un blog par niche avec liens
  affiliés Amazon.

  **Constat/challenge apporté** : le modèle "blog texte + affiliation
  Amazon" a beaucoup vieilli depuis l'époque probable de cette formation :
  - Mises à jour Google "Helpful Content" (2022-2024) pénalisent lourdement
    les sites d'affiliation minces sans preuve d'usage réel du produit.
  - Le contenu généré par IA a saturé ce créneau, rendant le SEO pur plus
    dur et plus concurrentiel qu'avant.
  - Les commissions Amazon ont baissé sur beaucoup de catégories (souvent
    1-4% aujourd'hui).
  - "Un site par niche" = fragile : dépendance à 100% à l'algorithme Google,
    une mise à jour peut effacer plusieurs sites d'un coup.

  **Pivot proposé — exclure Amazon, exploiter Affilae différemment** :
  privilégier les verticales à commission plus intéressante que le retail
  Amazon :
  - **CPA fixe par lead** (souvent le plus rentable) : assurance/mutuelle
    (20-80€/devis), comparateurs d'énergie (30-100€/contrat signé), banque
    en ligne/carte bancaire (20-50€/ouverture de compte), crédit immobilier.
  - **Commission récurrente mensuelle** : hébergement web, VPN, logiciels
    SaaS — revenu qui s'accumule tant que le client reste abonné, contrairement
    à un achat unique Amazon.
  - **Formations/coaching en ligne** : commissions souvent 20-50%, panier
    élevé (comme la formation Olivier Allain elle-même).

  **Différenciation proposée** : au lieu d'un blog texte classique (facilement
  copié par l'IA), construire un **outil interactif** par site (comparateur,
  questionnaire de recommandation type "quelle offre vous correspond ?") —
  s'appuie directement sur le pattern déjà éprouvé du widget "Live Test" de
  BlackBox (formulaire → traitement → résultat affiché). Google valorise ce
  type de contenu à valeur ajoutée réelle, difficile à reproduire par simple
  génération de texte IA.

  **Idée d'exécution rapide (pour ne pas reperdre des jours à chaque site)** :
  construire **un seul moteur générique réutilisable** une fois (design,
  structure, logique de questionnaire/recommandation), piloté par **un
  fichier de config JSON par niche** (questions du quiz, liste d'offres +
  liens d'affiliation + critères de recommandation, couleurs/branding). Le
  premier site demande un vrai investissement de construction ; chaque site
  suivant ne demande plus que de remplir ce fichier de config et déployer —
  quelques heures, pas des jours.

  **Prochaine étape suggérée (au bon moment, pas avant le lancement réel de
  BlackBox Labs — voir priorités ci-dessus)** : consulter le catalogue/
  marketplace Affilae, lister les 5-10 programmes qui paient le mieux par
  verticale, choisir une première niche avec Steve, puis démarrer la
  construction du moteur générique.

- (28/09) **Lecture critique d'un document "Venturlab" (7 modèles d'entreprise
  rentables) — un insight à retenir, la source à traiter avec prudence**

  **Contexte** : Steve a partagé un PDF marketing de Venturlab ("laboratoire
  de recherche en création d'entreprise") qui prétend avoir analysé 4 145
  entreprises pour identifier les 7 modèles les plus rentables pour un
  débutant, avec un algorithme propriétaire de "correspondance profil-concept"
  et un taux de "94% de réussite en Done-for-you". Origine précisée par Steve :
  document diffusé par Pierre Richet, un compte Instagram sur l'entrepreneuriat
  — cohérent avec l'analyse ci-dessous (contenu créateur/influenceur destiné
  à générer des leads, pas une étude d'un organisme de recherche indépendant).

  **Évaluation critique apportée** : ce document a la forme d'un rapport de
  recherche mais la fonction d'un tunnel de vente — chaque section se termine
  par un CTA vers une consultation offerte ("venturlab.co/mentorat"), porte
  d'entrée probable vers un coaching payant haut de gamme. Points de vigilance
  identifiés :
  - Le "94% de réussite" n'est jamais défini (premier euro ? entreprise
    rentable à 1 an, 3 ans ?) — invérifiable de l'extérieur.
  - L'algorithme "SCCP" (scores de compatibilité /100, pondérations
    précises) est une boîte noire propriétaire, présentée avec le vocabulaire
    de la rigueur scientifique mais sans aucune validation indépendante.
  - Biais de survivance explicitement reconnu par le document lui-même
    (corpus = entreprises déjà visibles/existantes uniquement) puis ignoré
    dans la suite des pourcentages très précis avancés.
  - Le tableau "entrepreneur intuitif vs analytique" est un faux dilemme
    construit pour légitimer leur méthode, avec des exemples historiques
    discutables (Bezos présenté comme ayant validé avant d'investir, ce qui
    est contestable historiquement).

  **Ce qui est réellement solide dans le contenu** (mais du bon sens business
  classique, pas une découverte propriétaire) : vendre cher à peu de clients
  plutôt que pas cher à beaucoup, privilégier le revenu récurrent, se
  positionner sur une niche nommable, offre productisée plutôt que devis sur
  mesure. Principes qu'on retrouve par exemple chez Alex Hormozi ("$100M
  Offers"), disponibles gratuitement ailleurs.

  **Insight actionnable retenu pour BlackBox** : dans leur classement des 7
  modèles, "Automatisation et agents IA pour PME" arrive 4ème (22/25) —
  diagnostiquer les processus manuels d'une PME et livrer des automatisations
  no-code/IA sous forme d'audit payant (3000-5000€) puis projet au forfait
  (10000-15000€). C'est un signal externe (même si la source est à prendre
  avec recul) que l'angle **conseil/implémentation B2B sur mesure autour de
  l'IA/automatisation** — en complément du produit API self-service actuel
  de BlackBox — est un positionnement à fort potentiel, cohérent avec ce que
  BlackBox sait déjà construire techniquement.

  **Conclusion** : ne pas payer pour le "mentorat" Venturlab sur la seule foi
  de ce document. Mais garder l'idée d'un service B2B (audit + implémentation
  d'automatisations pour PME) comme extension possible du positionnement
  BlackBox, à explorer plus tard aux côtés du produit API actuel.

- (01/10) **Objectif explicite de liberté financière (5000€/mois) — le
  constat "marché API limitant" se confirme et converge avec l'entrée du
  28/09 ci-dessus**

  **Origine** : Steve a demandé un plan point par point pour atteindre
  5000€/mois "le plus rapidement possible avec un fort potentiel à obtenir
  bien plus", puis a explicitement élargi la contrainte : "peu importe le
  domaine pourvu qu'il permet d'arriver à ce but... je ne veux pas me limiter
  à des API". Cette session confirme donc, de façon indépendante et à un
  mois d'écart, le même diagnostic que l'entrée Venturlab du 28/09.

  **Cadrage honnête donné en premier lieu** : à la date de cette discussion,
  Paddle est toujours en sandbox en production (`Paddle.Environment.set
  ('sandbox')` vérifié dans le code source live) — le CA réel est de 0€ tant
  que ce n'est pas basculé, indépendamment de toute stratégie de croissance.
  5000€/mois n'est réaliste sur 6-18 mois **que** combiné à une vraie
  distribution active, pas en configuration passive actuelle.

  **Pourquoi le marché "API pour développeurs" plafonne structurellement**
  (raisons détaillées apportées en session, en plus du constat déjà écrit
  le 28/09) :
  1. Le client type (un développeur) a les compétences pour recréer le
     produit lui-même — seul marché où c'est vrai aussi frontalement.
  2. Concurrence directe avec des infrastructures géantes qui offrent déjà
     l'équivalent gratuitement ou presque (AWS Rekognition, Google Cloud
     Vision, Stripe, Twilio, Cloudflare).
  3. Prix plafonné bas par construction ($12-29/mois) vs une PME qui paie
     50-300€/mois sans sourciller pour un logiciel métier qui lui fait
     gagner du temps/argent concret.
  4. Distribution lente et froide (SEO/communauté sur des mois) contre une
     PME locale qu'on peut appeler ou visiter le jour même.
  5. Absence de moat technique (déjà noté dans l'audit initial du site).

  **Domaines explicitement écartés** (mise en garde donnée pour protéger
  Steve de pistes à faible probabilité) : trading/crypto spéculatif (la
  majorité des particuliers perdent de l'argent à moyen terme — un pari,
  pas un métier), dropshipping/e-commerce générique sans budget ni
  expérience publicitaire, et tout schéma MLM/"opportunité d'affaires" avec
  frais d'entrée.

  **Piste retenue en priorité — Agence d'automatisation IA pour PME** (pas
  des APIs pour développeurs, de l'automatisation de processus métier pour
  des entreprises classiques) :
  - Cycle de vente court (semaines, pas mois) — démarchage direct d'
    entreprises avec un problème visible, pas de conversion anonyme sur
    internet.
  - Clients avec un vrai budget opérationnel.
  - 100% compatible avec les compétences déjà démontrées par Steve (auth,
    paiement, intégrations API, déploiement — exactement la boîte à outils
    nécessaire).
  - Capital de départ quasi nul.
  - Modèle économique éprouvé depuis des années (intégrateurs Zapier/Make),
    l'IA élargit simplement ce qui est automatisable.
  - Tarification type : mise en place 1500-5000€ + abonnement maintenance
    300-800€/mois/client.

  **Pistes secondaires évoquées** : SaaS vertical pour un métier précis
  (logiciel de planning/gestion pour un métier spécifique — kinés,
  artisans du bâtiment, fleuristes... — qui paie bien et compare à son
  métier, pas à "gratuit sur GitHub") ; agence de services tech productisée
  pour entreprises locales (cash le plus rapide, plafond plus bas sans
  sous-traitance).

  **Niche de démarrage choisie par défaut** (faute d'info sur un contact
  personnel existant dans un secteur donné — réversible si Steve a en fait
  un contact ailleurs) : **artisans du bâtiment** (plombiers, électriciens,
  serruriers) — trouvables partout via Google Maps/Pages Jaunes sans réseau
  requis, douleur concrète et universelle (appel manqué = client perdu),
  moins bombardés par des pitchs "agence IA" que les e-commerçants/startups.

  **Démo technique définie** : "relance automatique SMS pour appel manqué"
  via webhook Twilio + petit backend Node.js réutilisant le boilerplate
  existant (`00_MASTERBOILERPLATE_V6`) — même type d'architecture que les
  endpoints BlackBox actuels (webhook → traitement → réponse automatique).

  **Plan d'exécution suggéré pour démarrer** :
  1. Construire la démo technique (1-2 soirées de dev).
  2. Préparer un script de démonstration de 60 secondes (avant/après).
  3. Lister 15-20 artisans locaux via Google Maps avec numéro de téléphone.
  4. Démarcher par appel direct ou visite en personne (pas d'email froid) en
     montrant la démo sur téléphone.

  **Articulation avec BlackBox Labs** : pas d'abandon du produit actuel —
  une fois Paddle basculé en production, laisser BlackBox tourner en tâche
  de fond comme revenu passif secondaire, sans y réinvestir de temps de
  distribution active prioritaire. L'agence d'automatisation devient le
  moteur principal pour la vitesse, BlackBox reste un "bonus" qui
  s'additionne.

  **Limite méthodologique à noter** : les tentatives de vérifier des
  données de marché fraîches 2026 (Google, Bing, DuckDuckGo, Reddit) ont
  toutes échoué depuis cet environnement (accès bloqué). Le raisonnement
  ci-dessus s'appuie sur des principes économiques durables et le profil
  réel de Steve, pas sur des statistiques récentes vérifiées — à challenger
  avec de vraies données terrain dès les premiers retours clients.

  **Prochaine étape suggérée** : ne pas lancer avant d'avoir confirmé si
  Steve a un contact personnel dans un secteur précis (raccourcit
  énormément le premier cycle de vente) ; sinon, démarrer directement sur
  la niche artisans du bâtiment par défaut.

  **Mise à jour (01/10, même soirée) — niche réajustée + principe
  généralisé par Steve** : Steve tranche explicitement pour accélérer — pas
  question de réinvestir des semaines supplémentaires dans la croissance de
  BlackBox avant de pivoter. Il confirme vouloir quand même finaliser la
  bascule Paddle en production pour "avoir vraiment tout le circuit"
  terminé (cohérent avec la distinction : finir l'administratif, peu
  coûteux, vs arrêter d'investir du temps de distribution active). Il
  élargit aussi spontanément les secteurs cibles acceptables au médical/
  dentaire, au-delà des artisans du bâtiment.

  **Cabinets dentaires/médicaux promus en premier choix** (artisans du
  bâtiment redevient option de repli) : la réduction des rendez-vous
  manqués ("no-show") est une douleur déjà bien documentée et chiffrée dans
  ce secteur (un rendez-vous manqué coûte couramment 50-150€ de revenu
  perdu par créneau), budget admin plus stable qu'un artisan indépendant,
  et la même démo technique (rappel automatique SMS/email) s'y applique au
  moins aussi bien. Démo reframée en conséquence : système de rappel de
  rendez-vous (J-1 et/ou H-2h avant) plutôt que relance d'appel manqué.

  Steve formule ensuite le principe le plus net de toute cette réflexion :
  *"m'adresser à des développeurs directement c'est comme si je m'adressais
  à des concurrents beaucoup plus compétents que moi qui peuvent recréer
  mon produit sans se fatiguer. Il faut des clients qui ne soient pas de ce
  domaine."* Ça clôt aussi la piste crypto évoquée entre-temps : même
  l'endpoint le plus sophistiqué techniquement (`crypto_verify`, checksum
  réel sur 9+ chaînes) n'échappe pas au problème s'il est vendu à des
  développeurs/Web3 builders — public parmi les plus techniques qui soient.
  Vérification concrète faite en session : le package npm gratuit et
  open-source `multicoin-address-validator` (alias historique
  `WAValidator`) couvre une bonne partie du même terrain multi-chaînes et
  était encore republié en juin 2025 — preuve directe qu'un développeur n'a
  même pas besoin de "recréer" quoi que ce soit, juste de faire
  `npm install`.

  **Conclusion opérationnelle** : le critère de sélection de niche pour
  toute nouvelle piste (agence d'automatisation ou autre) est désormais
  explicite — **le client final ne doit structurellement pas savoir
  coder**, pas seulement "ne pas être un développeur professionnel". Ça
  verrouille le choix des cabinets dentaires/médicaux (et des PME non-tech
  en général) comme cible, et élimine définitivement toute tentation de
  repositionner BlackBox ou un de ses endpoints vers un public développeur/
  Web3, même sur la partie la plus technique du produit. Chantiers de
  distribution active BlackBox (lancements publics, SEO, outreach,
  pricing...) mis en pause en conséquence — pas supprimés, à reconsidérer
  si l'agence ne prend pas.

- (01/10, plus tard dans la soirée) **⚠️ Risque concurrentiel majeur détecté
  sur l'angle "rappels automatiques anti no-show" pour le médical/dentaire
  — Doctolib Pro**

  **Origine** : Steve a demandé une explication claire du projet médical
  pour bien comprendre de quoi il s'agit. En vérifiant (site officiel
  `info.doctolib.fr`, pas une simple supposition), constat clé : Doctolib
  Pro annonce accompagner **"des centaines de milliers de soignants"** en
  France chaque jour, avec une tarification **"100% des fonctionnalités en
  illimité"** (un seul abonnement tout compris, pas à la carte), et possède
  du contenu dédié sur son propre site pour la recherche "rappel sms" — donc
  très probablement déjà incluses pour la majorité du marché français.

  **Conséquence** : pitcher "rappels automatiques anti no-show" à un
  cabinet déjà client Doctolib reviendrait à proposer gratuitement ce qu'il
  possède déjà dans un outil qu'il paie pour autre chose — refus quasi
  garanti dès le premier appel commercial, et risque de valider la mauvaise
  hypothèse si on construit la démo avant de vérifier ça sur le terrain.

  **Mitigation adoptée — valider avant de construire** : avant tout
  développement, appeler/visiter 3-5 cabinets dentaires locaux et demander
  simplement s'ils utilisent déjà Doctolib, s'ils ont déjà des rappels
  automatiques, et ce qui leur manque encore administrativement. Coût quasi
  nul (quelques appels), évite de construire une démo pour un problème déjà
  résolu chez le prospect.

  **Pistes de repli si confirmé que Doctolib couvre déjà les rappels** (à
  arbitrer selon les retours terrain) :
  1. Changer d'angle **à l'intérieur du médical/dentaire** vers un besoin
     que Doctolib ne couvre probablement pas nativement : relance de
     "recall" (rappel du contrôle annuel/détartrage, pas juste confirmation
     de rendez-vous déjà pris), ou gestion automatisée des avis Google après
     visite.
  2. Redonner la priorité aux **artisans du bâtiment** comme niche de
     démarrage — aucun acteur dominant équivalent à Doctolib n'occupe ce
     terrain de la même façon, risque de redondance plus faible.

  **Principe général à retenir pour toute niche future** : systématiquement
  vérifier s'il existe déjà un acteur dominant qui résout le même problème
  en natif/inclus, avant de construire quoi que ce soit — pas seulement
  pour le médical, pour chaque secteur PME envisagé à l'avenir.

-
