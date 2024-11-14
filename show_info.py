import tkinter as tk
from pymongo import MongoClient

def afficher_nombre_elements():
    # Connexion à MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["aviation_logs"]

    # Obtenir tous les noms de collections et compter les documents dans chaque collection
    collections_info = {}
    for collection_name in db.list_collection_names():
        count = db[collection_name].count_documents({})
        collections_info[collection_name] = count

    # Créer la fenêtre Tkinter
    root = tk.Tk()
    root.title("Nombre d'éléments par collection")

    # Afficher chaque collection et son nombre d'éléments
    for collection_name, count in collections_info.items():
        label = tk.Label(root, text=f"Collection '{collection_name}': {count} éléments")
        label.pack(pady=5)

    # Bouton pour fermer la fenêtre
    close_button = tk.Button(root, text="Fermer", command=root.destroy)
    close_button.pack(pady=10)

    root.mainloop()

# Exécuter la fonction
afficher_nombre_elements()
