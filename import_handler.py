import file_handler  
import re

FORMATS_ATTENDUS = {
    "pilote": ["numPil","nomPil","naisPil","villePil"],     
    "vol": ["numVol","villeD","villeA" ,"dateD","HD time" ,"dateA","HA time" ,"numPil" ,"numAv"],        
    "avion": ["numAv","nomAv","capAv","villeAv"],      
    "client": ["numCl","nomCl","numRuelCl","nomRueCl","codePosteCl","vileCl"],     
    "reservation": ["numCl","numVol","classe","nbPlaces"] 
}

FORMAT_REGEX = {

    "pilote": [
        r"^\d{4}$",          # int de 4 caractères
        r"^[A-Za-z]+$",      # str
        r"^\d{4}$",          # int de 4 caractères
        r"^[A-Za-z]+$"       # str
    ],
    "vol": [
        r"^V\d{3}$",         # "V" suivi de int de 3 caractères
        r"^[A-Za-z]+$",      # str
        r"^[A-Za-z]+$",      # str
        r"^\d+/\d+/\d+$",  # int/int/int (ex : 23/04/07)
        r"^\d+:\d+$",    # int:int (ex : 18:00)
        r"^\d+/\d+/\d+$",  # int/int/int (ex : 23/04/07)
        r"^\d+:\d+$",    # int:int (ex : 18:00)
        r"^\d{4}$",          # int de 4 caractères
        r"^\d{3}$"           # int de 3 caractères
    ],
    "avion": [
        r"^\d{3}$",          # int de 3 caractères
        r".*",      
        r"^\d+$",          # int de 3 caractères
        r".*"       # str
    ],
    "client": [
        r"^\d{4}$",          # int de 4 caractères
        r".*",      # str
        r"^\d+$",            # int de taille variable
        r".*",      # str
        r"^\d+$",            # int de taille variable
        r".*"       # str
    ],
    "reservation": [
        r"^\d{4}$",          # int de 4 caractères
        r"^V\d{3}$",         # "V" suivi de int de 3 caractères
        r"^[A-Za-z]+$",      # str
        r"^\d+$"             # int de taille variable
    ]
}

def check_format(ligne, categorie):
    """
    Vérifie que chaque élément d'une ligne correspond au format attendu pour une catégorie donnée.

    :param ligne: Liste des éléments de la ligne à vérifier.
    :param categorie: Nom de la catégorie, utilisé pour obtenir les regex.
    :return: True si tous les éléments correspondent aux regex, sinon False.
    """
    # Obtenir les regex pour la catégorie
    regex_list = FORMAT_REGEX.get(categorie)
    
    # Vérifier chaque élément de la ligne avec la regex correspondante
    for i, valeur in enumerate(ligne):
        # Si la regex pour l'élément existe et que la valeur ne correspond pas, retourne False
        if not re.match(regex_list[i], valeur):
            return False
    
    return True  # Tous les éléments correspondent aux regex


def importer_fichier(db,dossier, fichier):
    """
    Importe un fichier spécifique en vérifiant son format et en le parcourant ligne par ligne.
    
    :param dossier: Le nom du dossier (catégorie) du fichier.
    :param fichier: Le nom du fichier à importer.
    :return: liste des fichiers non importés,dictionnaire des fichiers bien importés avec nombre d'éléments bien importés, déjà présents, et d'erreurs.
    """

    info_import={}
    # Vérifie le format attendu pour cette catégorie
    format_attendu = FORMATS_ATTENDUS.get(dossier)
    
    chemin_fichier = f"{dossier}/{fichier}"
    with open(chemin_fichier, 'r') as f:
        premiere_ligne = f.readline().strip().split("\t")
        if not check_format(premiere_ligne,dossier):
            info_import[chemin_fichier]="error"
            print("Erreur : {} n'as pas le bon format ({} éléments trouvés/{} attendus)".format(chemin_fichier,len(premiere_ligne),format_attendu))
        else:
            info_import[chemin_fichier]={"error":{},"good_import":0,"duplicate":0,"false_duplicate":{}}
            for ligne_num, ligne in enumerate(f, start=0):
                elements = ligne.strip().split("\t")
                
                # Vérifie le nombre de colonnes
                if not check_format(elements,dossier):
                    info_import[chemin_fichier]["error"][ligne_num]=ligne
                
                else :
                    result,old_line=importer_ligne_vers_db(db, elements, dossier)
                    if result == "bonne":
                        info_import[chemin_fichier]["good_import"]+=1
                    elif result == "double":
                        info_import[chemin_fichier]["duplicate"]+=1
                    elif result == "mauvais double":
                        info_import[chemin_fichier]["false_duplicate"][ligne_num]={"new":ligne,"old":old_line}



            file_handler.ajouter_hash(db,chemin_fichier,dossier)
    return info_import

def importer_ligne_vers_db(db, ligne, categorie):
    """
    Importe une ligne dans la collection MongoDB spécifiée par 'categorie'.
    Vérifie si un doublon existe et compare les données si nécessaire.

    :param db: Instance de la base de données MongoDB.
    :param ligne: Liste d'éléments représentant une ligne à importer.
    :param categorie: Nom de la collection MongoDB (catégorie) où importer la ligne.
    :return: Résultat de l'importation ('bonne', 'double', 'mauvais double').
    """
    format_attendu = FORMATS_ATTENDUS.get(categorie)
    collection = db[categorie]

    document = {format_attendu[i]: ligne[i] for i in range(len(ligne))}    
    if categorie=="reservation":
        collection.insert_one(document)
        return "bonne",None
    
    document["_id"]=ligne[0]
    doublon = collection.find_one({"_id": ligne[0]})

    # Accéder à la collection MongoDB correspondant à la catégorie

    # Chercher un doublon basé sur un identifiant unique (ex : première colonne)

    if doublon:
        # Si un doublon est trouvé, comparer les documents
        if doublon == document:
            return "double",None  # Doublon identique
        else:
            # Espace pour demander à l'utilisateur s'il veut remplacer ou conserver l'original
            # (Laisser vide pour l'instant)
            return "mauvais double",doublon  # Doublon non identique
    else:
        # Insérer le document dans la base de données
        collection.insert_one(document)
        return "bonne", None  # Importation réussie

def parcourir_verifier_importer(db):
    """
    Parcourt tous les éléments dans les dossiers, vérifie leurs hash et les importe.
    """
    import_log_collection = db["import_logs"]
    # Obtenir les nouveaux fichiers et ceux déjà importés
    import_log = file_handler.charger_import_log(import_log_collection)  # Chargement des logs actuels
    resultats = file_handler.analyser_dossiers(import_log)  # Analyse des dossiers

    # Parcours des nouveaux fichiers dans chaque catégorie
    info_import={}
    vol_info_import={}
    for dossier, fichiers in resultats.items():
        for fichier in fichiers["nouveaux"]:
            print(f"Traitement du fichier {fichier} dans le dossier {dossier}...")
            file_info_import = importer_fichier(db,dossier, fichier)
            info_import.update(file_info_import)
    for dossier, fichiers in resultats.items():
        if dossier=="vol":
            for fichier in fichiers["nouveaux"]:
                file_vol_info_import=traiter_vols(db,dossier+"/"+fichier)
                vol_info_import.update(file_vol_info_import)
    
    return (info_import,vol_info_import)

def traiter_vols(db, fichier):
    file_vol_info_import={}
    file_vol_info_import[fichier]={"error":{},"good_import":0,"duplicate":0}
    # Collection cible pour les vols enrichis
    vol_nosql_collection = db["vol_nosql"]
    
    with open(fichier, 'r') as f:
        for ligne_num, ligne in enumerate(f, start=0):
            elements = ligne.strip().split("\t")
            
            # Vérifier le format de la ligne
            if not check_format(elements, "vol"):
                print(f"Ligne {ligne_num} : format incorrect.")
                file_vol_info_import[fichier]["error"][ligne_num]=elements
                continue

            # Extraire les informations de base
            numVol, ville_depart,ville_arrivee, date_depart, heure_depart, date_arrivee, heure_arrivee, numPil, numAv = elements
            
            # Vérifier si le vol existe déjà
            vol_existant = vol_nosql_collection.find_one({"_id": numVol})
            if vol_existant:
                file_vol_info_import[fichier]["duplicate"]+=1
                continue
                
            # Construire le dictionnaire du vol avec les informations de base
            vol_document = {
                "_id": numVol,
                "ville_depart": ville_depart,
                "ville_arrivee": ville_arrivee,
                "date_depart": date_depart,
                "heure_depart": heure_depart,
                "date_arrivee": date_arrivee,
                "heure_arrivee": heure_arrivee
            }
            
            # Récupérer et remplacer les informations du pilote
            pilote_info = db["pilote"].find_one({"numPil": numPil})
            if pilote_info:
                # Retirer `_id` pour éviter les conflits
                pilote_info.pop("_id", None)
                vol_document["pilote"] = pilote_info
            else:
                print(f"Ligne {ligne_num} : pilote {numPil} introuvable.")
                continue

            # Récupérer et remplacer les informations de l'avion
            avion_info = db["avion"].find_one({"numAv": numAv})
            if avion_info:
                avion_info.pop("_id", None)
                vol_document["avion"] = avion_info
            else:
                print(f"Ligne {ligne_num} : avion {numAv} introuvable.")
                continue

            # Ajouter les réservations avec leurs informations client
            reservations = {}
            for reservation in db["reservation"].find({"numVol": numVol}):
                numCl = reservation.get("numCl")
                
                # Récupérer les informations du client
                client_info = db["client"].find_one({"numCl": numCl})
                if client_info:
                    client_info.pop("_id", None)
                    # Ajouter les informations client à la réservation
                    reservation["client"] = client_info
                    reservation_id = str(reservation["_id"])
                    # Ajouter la réservation au dictionnaire avec l'ID MongoDB comme clé
                    reservations[reservation_id] = reservation
                else:
                    print(f"Ligne {ligne_num} : client {numCl} introuvable pour la réservation.")
            
            # Ajouter toutes les réservations enrichies au document du vol
            vol_document["reservations"] = reservations
            
            # Insérer le vol enrichi dans la collection `vol_nosql`
            vol_nosql_collection.insert_one(vol_document)
            file_vol_info_import[fichier]["good_import"]+=1
            print(f"Ligne {ligne_num} : vol {numVol} ajouté avec succès.")
    
    return (file_vol_info_import)

def import_all(db):
    """
    Fonction principale d'importation qui appelle toutes les étapes nécessaires.
    """
    print("Début de l'importation...")
    info_import, vol_info_import= parcourir_verifier_importer(db)
    # Appel aux autres étapes (à implémenter dans la suite)
    print("Importation terminée.")
    return(info_import,vol_info_import)
    
