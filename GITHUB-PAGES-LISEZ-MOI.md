# Publication de pharma-store sur GitHub Pages

Cette archive conserve **tous les fichiers Django originaux** et ajoute `index.html` à la racine pour éviter le 404 sur GitHub Pages.

## Mise en ligne
1. Décompressez le ZIP.
2. Sur GitHub > pharma-store, ajoutez **le contenu** du dossier `pharma-store-github-ready` à la racine de la branche `main` (pas le dossier parent).
3. Confirmez que `index.html` apparaît au même niveau que `manage.py`.
4. Settings > Pages : Deploy from branch, `main`, `/(root)`.
5. Ouvrez https://boumiza-1.github.io/pharma-store/ après le déploiement.

## Limites
GitHub Pages héberge uniquement des fichiers statiques. La page créée est un **aperçu autonome** avec recherche, filtre et panier de démo non persistant. Elle ne représente pas le catalogue de production. Les comptes clients, produits de la base, commandes, authentification et administration Django ne peuvent pas être actifs sans serveur Python + base de données. N'utilisez pas les écrans de démo pour de vrais achats.
