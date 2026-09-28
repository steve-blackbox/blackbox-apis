# BlackBox Labs — Repository Instructions for Copilot

Ce fichier documente les règles fixes du projet pour que l'agent n'ait pas à les
redécouvrir à chaque session. Le propriétaire (Steve) parle français ; répondre
en français par défaut.

## Contexte produit
- BlackBox Labs est un SaaS d'APIs développeur (12 utilitaires réels répartis en
  3 catégories : Privacy & PII Protection, Security & Link Integrity, Data &
  Media Utilities).
- Le site est servi par `server.js` (Express) et déployé sur **Render**, avec
  **GitHub** comme dépôt source.
- Le repo racine de travail est `01_LA_SOUTE_A_CASH/` (le dossier parent
  `Copie_de_TRAVAIL_BlackBoxLocal` n'est pas lui-même un dépôt Git).

## Git — workflow réel (pas de Pull Request)
- Le propriétaire pousse **directement sur `main`**, sans branches de travail
  ni Pull Requests. Ne jamais proposer/utiliser `create-pr`, `merge`, `sync`,
  ni un flux de branches — ce n'est pas comment ce projet fonctionne.
- Toujours committer avec un message clair (voir style des commits existants
  avec `git log --oneline`) puis `git push origin main` seulement après
  confirmation explicite de l'utilisateur ("on pousse", "pousse", etc.).
- Ne jamais pousser sans demande explicite au préalable.

## Serveur local (développement)
- `server.js` plante au démarrage sans la variable d'environnement
  `RESEND_API_KEY` (le client Resend lève une exception si elle est absente).
- Pour lancer le serveur en local uniquement à des fins de test (ne jamais
  committer de vraie clé) :
  ```bash
  RESEND_API_KEY=re_test_dummy_key PORT=8080 node server.js
  ```
- Le site tourne alors sur `http://localhost:8080/`.

## Clé de démonstration publique
- `BB-DEMO-POSTMAN-PUBLIC01` est la clé de licence publique utilisée par le
  widget "Live Test" du site pour appeler les vrais endpoints depuis le
  navigateur d'un visiteur. Limite serveur : 50 requêtes/jour
  (`DEMO_DAILY_LIMIT` dans `server.js`). Ne jamais la faire passer pour une
  clé secrète — elle est volontairement publique et plafonnée.

## Footer légal — NE JAMAIS SUPPRIMER
- Le footer de `public/index.html` contenant "Terms of Service", "Refund
  Policy", "Privacy Policy" et "Contact / Support" est marqué dans le code
  comme `MICRO-FOOTER DE COMPLIANCE MANDATAIRE PADDLE & MERCURY`.
- Paddle et Mercury (processeurs de paiement) exigent que ces liens légaux
  restent visibles directement en bas de page (pas seulement dans un menu),
  dans le cadre de la vérification KYB (Know Your Business).
- Ne jamais retirer ou masquer ce footer, même si un lien équivalent existe
  ailleurs (ex. menu de navigation) — sauf confirmation explicite et réfléchie
  de l'utilisateur, qui a déjà été prévenu du risque une fois.

## Paiements — état du projet
- **Paddle** : compte en cours de vérification (KYB). Vérifier le vrai statut
  se fait dans le dashboard Paddle (Settings/Business details), pas dans
  l'assistant d'onboarding "agent IA" qui peut afficher 0% même si la vraie
  demande est en cours ailleurs.
- **RapidAPI → PayPal → Wise** : circuit d'encaissement configuré et actif
  (compte Wise enregistré sur PayPal, virements automatiques activés).
- Je n'ai accès à aucun compte externe (Paddle, PayPal, Render, RapidAPI) —
  je ne peux ni m'y connecter ni les configurer à la place de l'utilisateur.

## Structure du site (`public/`)
- `index.html` : page principale, structure en 3 "screens" verticaux
  (`#screen-command` hero, `#screen-playground` carrousel horizontal des 3
  catégories de robots, `#screen-payment` pricing) + `terms.html`,
  `privacy.html`, `docs.html`.
- `style.css` : tout le CSS du site (~3600+ lignes). Toujours vérifier
  l'équilibre des accolades après édition :
  `grep -o '{' public/style.css | wc -l` doit égaler
  `grep -o '}' public/style.css | wc -l`.
- Le footer et certains blocs (`stripe-section`, `license-ingress`) sont
  déplacés dynamiquement en JS via `composeScreenSections()` — si un nouveau
  bloc doit apparaître entre eux dans le DOM final, il faut l'ajouter à la
  liste `[stripe, ingress, footer].forEach(...)` (ou équivalent) et non se
  fier uniquement à l'ordre dans le HTML source.

## Diagnostic visuel — méthode qui a fait ses preuves
- Pour les bugs de layout (espace mort, bandes de couleur, débordement),
  utiliser `getBoundingClientRect()` / `document.documentElement.scrollHeight`
  via le navigateur pour mesurer précisément avant de corriger à l'aveugle.
- Pour confirmer visuellement une différence de couleur de fond entre deux
  zones, échantillonner les pixels d'une capture d'écran (PIL/Python) plutôt
  que de se fier à l'œil seul.
- Pour tester une hypothèse de correctif CSS avant de l'appliquer au fichier,
  utiliser `element.style.setProperty(prop, val, 'important')` — un style
  inline sans priorité `important` ne bat pas un `!important` déjà présent
  dans la feuille de style.

## Autres documents du repo
- `PROJETS_FUTURS.md` : idées business "someday/maybe" (sites d'affiliation
  par niche, extension B2B automatisation/IA). Ne jamais commencer à
  construire ces projets sans demande explicite — la priorité reste le
  lancement de BlackBox Labs.
- `README_TRACKING.md` : tableau de bord de traction (checkpoints J+30/60/90).
  Point important non résolu : le disque persistant Render
  (`data/blackbox.db`) doit être configuré avant le lancement réel, sinon
  l'historique des ventes est effacé à chaque redéploiement.
