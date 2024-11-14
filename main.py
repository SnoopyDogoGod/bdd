import file_handler
import interface_handler
from pymongo import MongoClient

if __name__=="__main__" :


    client = MongoClient("mongodb://localhost:27017/")
    db = client["aviation_logs"]

    for collection_name in db.list_collection_names(): #pour tests
        db[collection_name].drop()

    
    file_handler.verifier_et_creer_dossiers()


    interface_handler.lancer_interface(db)