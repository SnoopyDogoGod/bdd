# Projet d'Intégration de Données de Vol

Ce projet permet d'importer, enrichir, et visualiser des données de vol, client, avion, pilote, et réservation dans une base de données MongoDB, avec une interface graphique pour suivre et contrôler l'importation.

## Prérequis

- **Python** : Assurez-vous que Python est installé.
- **Dépendances** : Installez les modules Python nécessaires avec :
  ```bash
  pip install pymongo tkinter redis

    MongoDB : MongoDB doit être lancé et accessible sur localhost:27017.
    Redis (optionnel) : Si Redis est utilisé, assurez-vous qu'il est configuré sur localhost:6379.

## Mise en Place des Fichiers

    Placez les fichiers .txt d'exemple (vol, client, avion, pilote, réservation) dans leurs dossiers respectifs :
        data/pilote
        data/vol
        data/avion
        data/client
        data/reservation

    Ces fichiers d'exemple contiennent plusieurs types de données pour simuler les imports.  
    **Tout l'intéret du projet est de lancer le programme plusieurs fois, en ajoutant des fichiers à chaque fois pour les intégrer**

## Lancer le Projet

    Exécutez le fichier principal avec :

    python main.py

    Une interface graphique s'ouvre, affichant les fichiers détectés dans chaque dossier.

## Utilisation de l'Interface

    Importer les Données : Cliquez sur le bouton "Importer tous les nouveaux éléments" pour lancer l'importation des fichiers détectés dans MongoDB.
    Visualiser les Résultats : Après l'import, scrollez vers le bas pour consulter les statistiques et les détails d'importation, y compris les erreurs, doublons, et faux doublons.

## Informations Supplémentaires

Ce projet est conçu pour un import progressif, permettant d’ajouter des fichiers de manière différée et de visualiser l'état de chaque fichier importé. Plusieurs fichiers de test sont inclus pour différents types de données, permettant de simuler des imports partiels et de tester la gestion des erreurs et des doublons.
