__Corentin Ghyselinck__
__Julien Schametz__
__Alexis Braibant__

-----------------

Scenario utilisateur:

1. Lancer l'application, choisir le dossier test1 et test2, (il y a déjà des changements de base).

2. Appuyer sur "lancer la synchronisation continue", le dossier test2 est maintenant un mirroir du dossier1.

3. Écrire "pdf" dans "Extension" et modifier un fichier txt, on peut voir que le fichier txt n'est pas modifié dans le dossier de destination car le filtre ne modifie que les pdf dans ce cas, "arrêter la synchronisation continue" avec le bouton du même nom.

4. Modifier un fichier du dossier test1, appuyer sur "Sauvegarder état dans la BDD".
L'écran du bas devrais afficher le chemin du fichier modifié, ses informations son sauvegardées dans la BDD.

5. Modifier un deuxième fichier puis appuyer sur "Maj fichiers avec BDD", le premier fichier modifié est bien modifié dans le dossier de destination mais pas le deuxieme car il a été modifié après la sauvegarde.

-----------------

Utilisation : `python main.py`

-----------------

Explication de l'interface graphique:

Bouton Dossier source : Permet de choisir le dossier source (obligatoire).
Bouton Dossier de destination : Permet de choisir le ossier de destination (obligatoire).

Extension(pdf,txt): Permet d'ajouter un filtre à la synchronisation continue (optionnel).

Lancer la syncrhonisation continue: Ce bouton lance une synchronisation du dossier source vers le dossier de destination toutes les X secondes.
Arrêter la syncrhonisation continue : Ce bouton arrête la synchronisation .

Sauvegarder état dans la BDD: Envoi vers un fichier folders.db les informations nécessaire à la reprise de la synchronisation, le chemin relatif et absolu ainsi qu'un hash de chaque fichier qui permet de détecter une modification (aucun contenue direct donc).

Elle affiche en bas les différences entre le dossier source et destination, pour tester, modifier un fichier dans le dossier source et appuyer sur le bouton.

Maj fichiers avec la BDD : mettre à jour le dossier de destination avec uniquement une copie des fichiers qui étaient différents au moment de la sauvegarde.

Quitter: fermer l'application proprement.

