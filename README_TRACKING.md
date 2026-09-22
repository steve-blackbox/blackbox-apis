# 📊 Tableau de bord de traction — BlackBox

Outil intégré au code pour suivre en temps réel les indicateurs des checkpoints
J+30 / J+60 / J+90 définis dans la ligne directrice
(`utiles/ligne_directrice_strategie.md`).

Deux volets, comme convenu :
1. **Ventes / revenus** → suivi interne (base SQLite embarquée dans le serveur).
2. **Trafic / visiteurs** → outil tiers gratuit (Umami), plus fiable dans la durée.

---

## 1. Ventes & revenus (déjà actif dès le prochain déploiement)

- Chaque paiement Stripe confirmé (`checkout.session.completed`) est automatiquement
  enregistré dans `data/blackbox.db` (email, plan, montant, date).
- Consultez le tableau de bord à l'adresse : `https://votre-domaine/admin/dashboard`
- Il vous demandera une **clé admin** : elle est définie par la variable d'environnement
  `ADMIN_DASHBOARD_KEY` (déjà générée dans `.env` local — à reporter dans les variables
  d'environnement Render pour la production).
- Le tableau affiche : jour depuis le lancement, statut du checkpoint (GO / ZONE_GRISE /
  NO_GO / ALERTE...), revenu total, revenu 30 derniers jours, détail par offre, 20 dernières ventes.

### ⚠️ Important : persistance des données sur Render
Le fichier `data/blackbox.db` est stocké sur le disque du serveur. **Render efface ce
disque à chaque redéploiement**, sauf si vous ajoutez un **Persistent Disk** :
`Render Dashboard → votre service → Disks → Add Disk`, monté sur le chemin `/opt/render/project/src/data`
(ou l'équivalent du dossier `data/` de ce projet). Sans ce disque, l'historique des
ventes repart de zéro à chaque déploiement — à faire avant le lancement réel.

### Variables d'environnement à définir sur Render
| Variable | Rôle |
|---|---|
| `ADMIN_DASHBOARD_KEY` | Clé secrète pour accéder au tableau de bord |
| `LAUNCH_DATE` (optionnel) | Force la date J0 des checkpoints (format `YYYY-MM-DD`). Si absente, elle se fixe automatiquement au premier démarrage. |

---

## 2. Trafic & visiteurs (Umami — à activer manuellement)

Le script est déjà inséré dans `public/index.html` mais **désactivé** tant que l'ID
n'est pas renseigné :

```html
<script defer src="https://cloud.umami.is/script.js" data-website-id="YOUR-WEBSITE-ID"></script>
```

### Étapes pour l'activer (5 minutes) :
1. Créez un compte gratuit sur [cloud.umami.is](https://cloud.umami.is).
2. Ajoutez votre site (URL du domaine BlackBox).
3. Copiez l'ID du site fourni par Umami.
4. Remplacez `YOUR-WEBSITE-ID` dans `public/index.html` par cet ID.
5. Le trafic (visiteurs, pages vues, sources) apparaît alors directement dans votre
   tableau de bord Umami — utilisez-le pour valider le critère "trafic" du checkpoint J+30.

---

## Résumé du parcours de décision (rappel)

| Checkpoint | Ce qu'il faut regarder | Où |
|---|---|---|
| J+30 | Visiteurs, taux de clic, inscriptions | Umami |
| J+60 | Premiers clients payants, revenu ≥ 50-150 € | `/admin/dashboard` |
| J+90 | Revenu ≥ 300-500 €/mois → GO ; 50-300 € → zone grise ; < 50 € → NO_GO | `/admin/dashboard` |
| Continu | Moyenne glissante 6 mois ≥ 4750-5000 €/mois → seuil de démission | `/admin/dashboard` + `utiles/suivi_seuil_demission.xlsx` |
