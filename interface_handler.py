import tkinter as tk
from tkinter import Frame, Label, Scrollbar, Text, Button, ttk
import file_handler  # Import du module file_handler
import import_handler
# Fonction pour initialiser l'interface Tkinter
def initialiser_interface():
    root = tk.Tk()
    root.title("Suivi des fichiers d'importation")
    root.geometry("2300x550")
    return root

def actualiser_affichage(root,db):
    import_log_collection = db["import_logs"]
    import_log = file_handler.charger_import_log(import_log_collection)

    # Efface les anciens widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Titre des colonnes
    for i, dossier in enumerate(file_handler.dossiers):
        Label(root, text=dossier.upper(), font=("Arial", 12, "bold")).grid(row=0, column=i+1, pady=(5, 10))

    Label(root, text="Nouveaux fichiers", font=("Arial", 12, "bold")).grid(row=1, column=0, pady=(5, 10))
    Label(root, text="Fichiers déjà importés", font=("Arial", 12, "bold")).grid(row=2, column=0, pady=(5, 10))

    # Analyse les dossiers pour déterminer les nouveaux fichiers et les fichiers importés
    resultats = file_handler.analyser_dossiers(import_log)

    # Création des zones de texte défilantes pour chaque colonne et chaque ligne (nouveau / déjà importé)
    for i, dossier in enumerate(file_handler.dossiers):
        nouveaux_fichiers = resultats[dossier]["nouveaux"]
        fichiers_importes = resultats[dossier]["importes"]

        # Création de la zone défilante pour les nouveaux fichiers
        frame_nouveaux = Frame(root)
        frame_nouveaux.grid(row=1, column=i+1, padx=5, pady=5, sticky="nsew")

        scrollbar_nouveaux = Scrollbar(frame_nouveaux, orient="vertical")
        text_nouveaux = Text(frame_nouveaux, height=5, width=20, fg="red", yscrollcommand=scrollbar_nouveaux.set, wrap="none")        
        scrollbar_nouveaux.config(command=text_nouveaux.yview)
        scrollbar_nouveaux.pack(side="right", fill="y")
        text_nouveaux.pack(side="left", fill="both", expand=True)

        # Ajoute les nouveaux fichiers dans la zone de texte
        for fichier in nouveaux_fichiers:
            text_nouveaux.insert(tk.END, fichier + "\n")
        text_nouveaux.config(state="disabled")  # Rendre la zone de texte en lecture seule

        # Création de la zone défilante pour les fichiers déjà importés
        frame_importes = Frame(root)
        frame_importes.grid(row=2, column=i+1, padx=5, pady=5, sticky="nsew")

        scrollbar_importes = Scrollbar(frame_importes, orient="vertical")
        text_importes = Text(frame_importes, height=5, width=20, fg="green", yscrollcommand=scrollbar_importes.set, wrap="none")        
        scrollbar_importes.config(command=text_importes.yview)
        scrollbar_importes.pack(side="right", fill="y")
        text_importes.pack(side="left", fill="both", expand=True)

        # Ajoute les fichiers importés dans la zone de texte
        for fichier in fichiers_importes:
            text_importes.insert(tk.END, fichier + "\n")
        text_importes.config(state="disabled")  # Rendre la zone de texte en lecture seule

    bouton_importer = Button(root, text="Importer tous les nouveaux éléments", command=lambda:actualiser_et_afficher_resume(root,db))
    bouton_importer.grid(row=3, column=0, pady=10)
    # Rafraîchit l'interface toutes les secondes
    #root.after(1000, lambda: actualiser_affichage(root,db))

def actualiser_et_afficher_resume(root,db):
    # Appeler la fonction d'importation
    info_import,vol_info_import = import_handler.import_all(db)
    
    # Rafraîchir l'affichage principal
    actualiser_affichage(root, db)
    
    # Afficher le résumé de l'importation
    afficher_resume_importation(info_import,vol_info_import)
    
    

def afficher_resume_importation(info_import,vol_info_import):
    # Créer la fenêtre de résumé
    root = tk.Tk()
    root.title("Résumé de l'Importation")

    # Cadre principal défilant
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Configuration du canvas pour le défilement
    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Variables de résumé global
    total_fichiers = 0
    total_good_import = 0
    total_duplicates = 0
    total_false_duplicates = 0
    total_errors = 0
    # Afficher les détails pour chaque fichier
    for fichier, resultats in info_import.items():
        total_fichiers += 1
        
        # Nom du fichier
        fichier_label = tk.Label(scrollable_frame, text=f"Fichier : {fichier}", font=("Arial", 12, "bold"))
        fichier_label.pack(anchor="w", pady=(10, 0))
        
        # Vérifier le statut de l'import
        if resultats == "error":
            error_label = tk.Label(scrollable_frame, text="❌ Erreur lors de l'import", fg="red")
            error_label.pack(anchor="w", padx=20)
            total_errors += 1
        else:
            # Résumé des bons imports, doublons, et faux doublons
            total_good_import += resultats["good_import"]
            total_duplicates += resultats["duplicate"]
            total_false_duplicates += len(resultats["false_duplicate"])
            if resultats['good_import']>0:
                good_label = tk.Label(scrollable_frame, text=f"✅ Bonnes importations : {resultats['good_import']}", fg="green")
                good_label.pack(anchor="w", padx=20)

            if resultats['duplicate']>0:
                duplicate_label = tk.Label(scrollable_frame, text=f"⚠️ Doublons : {resultats['duplicate']}", fg="orange")
                duplicate_label.pack(anchor="w", padx=20)
            if resultats['false_duplicate']:
                false_duplicate_label = tk.Label(scrollable_frame, text=f"❌ Faux doublons : {len(resultats['false_duplicate'])}", fg="red")
                false_duplicate_label.pack(anchor="w", padx=20)
            
            if resultats['error']:
                false_duplicate_label = tk.Label(scrollable_frame, text=f"❌ Erreurs : {len(resultats['error'])}", fg="red")
                false_duplicate_label.pack(anchor="w", padx=20)

            # Afficher les erreurs spécifiques avec bouton Détails
            if resultats["error"]:
                error_button = tk.Button(scrollable_frame, text="Voir les erreurs", command=lambda r=resultats["error"]: afficher_erreurs(r))
                error_button.pack(anchor="w", padx=40)

            # Afficher les faux doublons spécifiques avec bouton Détails
            if resultats["false_duplicate"]:
                false_dup_button = tk.Button(scrollable_frame, text="Voir les faux doublons", command=lambda fd=resultats["false_duplicate"]: afficher_erreurs(fd))
                false_dup_button.pack(anchor="w", padx=40)

    
    # Section pour afficher les informations d'importation du vol
    vol_label = tk.Label(scrollable_frame, text="Vols Importés", font=("Arial", 12, "bold"))
    vol_label.pack(anchor="w", pady=(10, 0))

    for fichier, resultats in vol_info_import.items():
        fichier_label = tk.Label(scrollable_frame, text=f"Fichier : {fichier}", font=("Arial", 12, "bold"))
        fichier_label.pack(anchor="w", pady=(10, 0))
        # Afficher les bons imports, les doublons et les erreurs pour les vols
        vol_good_label = tk.Label(scrollable_frame, text=f"✅ Bonnes importations : {resultats['good_import']}", fg="green")
        vol_good_label.pack(anchor="w", padx=20)

        if resultats['duplicate']>0:
            vol_duplicate_label = tk.Label(scrollable_frame, text=f"⚠️ Doublons : {resultats['duplicate']}", fg="orange")
            vol_duplicate_label.pack(anchor="w", padx=20)

        # Si des erreurs existent dans vol_info_import["error"], afficher le bouton pour les détails
        if resultats["error"]:
            vol_error_label = tk.Label(scrollable_frame, text="❌ Erreurs d'importation :", fg="red")
            vol_error_label.pack(anchor="w", padx=20)
            vol_error_button = tk.Button(scrollable_frame, text="Voir les erreurs", command=lambda: afficher_erreurs(resultats["error"]))
            vol_error_button.pack(anchor="w", padx=40)
    # Résumé global en bas
    global_summary = tk.Label(
        scrollable_frame,
        text=(
            f"\nRésumé Global :\n"
            f"Total fichiers traités : {total_fichiers}\n"
            f"Total nouvelles importations : {total_good_import}\n"
            f"Total doublons : {total_duplicates}\n"
            f"Total erreurs : {total_errors}\n"
            f"Total faux-doublons : {total_false_duplicates}\n"

            
        ),
        font=("Arial", 12, "bold")
    )
    global_summary.pack(anchor="w", pady=(20, 10))

    # Bouton de fermeture
    close_button = tk.Button(root, text="Fermer", command=root.destroy)
    close_button.pack(pady=10)

    root.mainloop()

def afficher_erreurs(erreurs):
    # Créer une nouvelle fenêtre pour afficher les erreurs détaillées
    error_window = tk.Toplevel()
    error_window.title("Détails des Erreurs")

    for ligne, contenu in erreurs.items():
        if isinstance(contenu, dict):
            erreur_label = tk.Label(error_window, text=f"Ligne {str(ligne).ljust(5)} : Nouveau contenu : {str(contenu['new']).ljust(20)}  Contenu actuel : {'\t'.join(map(str, contenu['old'].values()))}")
        else:
            erreur_label = tk.Label(error_window, text=f"Ligne {ligne} : {contenu}")
        erreur_label.pack(anchor="w", padx=10, pady=2)


# Fonction principale pour lancer l'interface
def lancer_interface(db):
    root = initialiser_interface()
    actualiser_affichage(root,db)
    root.mainloop()
