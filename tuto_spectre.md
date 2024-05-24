# Tuto spectre in virtuoso

## Comment simuler une grille de résistances avec des tensions d’entrée custom :

### Méthodologie : 
Créer une nouvelle librairie
Créer une nouvelle cellview
Créer une vue spectre dans cette cellview et y copier le résultat du script Python mnist_rram.py

A partir d’ici je pense qu’il y a un moyen de faire directement la simulation mais je propose la version qui a marché pour moi :

Créer une vue symbol à partir de la vue spectre dans Create/cell view from cell view
Créer une nouvelle cellview dans la libraire 
Créer une vue schematic et poser le symbole dedans
Relier toutes les pins générées automatiquement à des analogLib/gnd
Créer une vue config dans la cellview -> Use template -> Spectre et choisir view to use : Spectretext
Ne pas oublier de check and save à chaque étape
Ouvrir ADE L ou ADE Explorer depuis la vue config
Choisir le simulateur spectre et pas ams dans Setup/simulator
Si erreur à ce moment là relancer virtuoso
Choisir les paramètres de simulation et signaux à enregistrer (ici les courants COL) : prendre tran et le temps que l'on souhaite il faut juste avoir plus de 5 instants de simulation pour que adc.py fonctionne (peut être modifié)
Sauvegarder le script Ocean DANS LE DOSSIER OU ON A LANCE VIRTUOSO en allant dans session->... script Ocean
Dans mon cas, enlever la ligne processOption
Enlever ou commenter à l’aide de ; les plot
ajouter outputs() qui affichera dans les logs les différents signaux que l’on peut sauvegarder
Ajouter les commandes ocnPrint(? output “/path/to/result/file” ?step 1m ?numSpaces 1 ?precision 5 ?numberNotation ‘none i(“/I0/COL_000”) …. i(“/I0/COL_099)) (on peut changer les paramètres selon ce qu’on veut conserver)
Pareil pour les COLN (pour moi dans un autre fichier mais pas obligatoire)
Ajouter exit()
Aller dans le terminal sourcé et lancer ocean < ./scriptOcean > logfile.log
Vérifier qu’il n’y a pas d’erreurs dans le log
Récupérer les deux fichiers texte
Modifier les path/to/file dans le script adc.py (skip 5 lignes et prend la première)
On obtient normalement la liste des courants (courants négatifs compris)

Je fournis un scriptOcean.ocn pour référence ainsi que deux fichiers qui donnent les courants sur les colonnes. 

Pour améliorer cette méthode : 

- Il faut trouver une manière de descendre dans la hierarchie quand on accède aux courants dans la cellview. Hypothèse : les nets que l'on save dans le scripts sont ceux de la vue schematic, il faudrait trouver un moyen de save ceux de la vue spectreText. 
