import hashlib
import os

# Dossiers à surveiller
dossiers = ["pilote", "vol", "avion", "client", "reservation"]

def verifier_et_creer_dossiers():
    # Variable pour suivre si des dossiers ont été créés
    tout_existe = True

    # Vérifie et crée chaque dossier
    for dossier in dossiers:
        if not os.path.exists(dossier):
            os.makedirs(dossier)
            tout_existe = False  # Indique qu'au moins un dossier a été créé

    return tout_existe

# Fonction pour calculer le hash d'un fichier
def calculer_hash(fichier):
    hasher = hashlib.md5()
    with open(fichier, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Chargement des hashes déjà importés depuis MongoDB
def charger_import_log(import_log_collection):
    """
    Charge les hashes de la collection MongoDB spécifiée.

    :param import_log_collection: Collection MongoDB où sont stockés les logs de hash.
    :return: Dictionnaire des fichiers avec leurs hashes.
    """
    import_log = {}
    for doc in import_log_collection.find():
        import_log[doc["_id"]] = {"hash":doc["_id"],"categorie":doc["categorie"],"fichier":doc["fichier"]}
    return import_log

# Enregistrement d'un hash dans MongoDB
def enregistrer_import_log(import_log_collection, fichier, hash_fichier, categorie):
    """
    Enregistre un hash dans la collection MongoDB spécifiée s'il n'est pas déjà présent.

    :param import_log_collection: Collection MongoDB où les logs de hash seront stockés.
    :param fichier: Nom du fichier à enregistrer.
    :param hash_fichier: Hash du fichier.
    """
    # Vérifie si le hash est déjà présent dans MongoDB
    if not import_log_collection.find_one({"_id": hash_fichier}):
        import_log_collection.insert_one({"_id": hash_fichier,"fichier": fichier, "categorie": categorie})

def ajouter_hash(db,fichier,categorie):
    hash_fichier = calculer_hash(fichier)
    import_log_collection=db["import_logs"]
    enregistrer_import_log(import_log_collection,fichier,hash_fichier,categorie)
    

# Fonction pour obtenir les nouveaux fichiers et les fichiers déjà importés dans chaque dossier
def analyser_dossiers(import_log):
    """
    Analyse les dossiers pour identifier les nouveaux fichiers et ceux déjà importés.

    :param import_log_collection: Collection MongoDB où sont stockés les logs de hash.
    :return: Dictionnaire contenant les nouveaux fichiers et ceux déjà importés par dossier.
    """
    # Charge les logs actuels depuis MongoDB
    resultats = {}

    # Parcourt chaque dossier pour analyser les fichiers
    for dossier in dossiers:
        nouveaux_fichiers = []
        fichiers_importes = []

        # Liste tous les fichiers du dossier


        for fichier in os.listdir(dossier):
            chemin_fichier = os.path.join(dossier, fichier)
            if os.path.isfile(chemin_fichier):
                hash_fichier = calculer_hash(chemin_fichier)
                # Vérifie si le hash est déjà dans le log d'import pour cette catégorie
                if hash_fichier in import_log and import_log[hash_fichier]["categorie"] == dossier:
                    fichiers_importes.append(fichier)
                else:
                    nouveaux_fichiers.append(fichier)

        
        # Stocke les résultats pour chaque dossier
        resultats[dossier] = {
            "nouveaux": nouveaux_fichiers,
            "importes": fichiers_importes
        }
    
    return resultats
