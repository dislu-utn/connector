#https://docs.cloud.google.com/firestore/native/docs/manage-data/add-data?hl=es-419

from typing import Literal
from google.cloud import firestore
from dotenv import load_dotenv
import os

import base64
import hashlib
from cryptography.fernet import Fernet

class Database:
    def __init__(self):
        load_dotenv()   
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        self.secret_key = os.getenv("SECRET_KEY")
        self.client = firestore.Client(project=os.getenv("PROJECT_ID"))
    
    def get_record(self, service_id="", service=Literal["dislu", "adaptaria"]):
        record = (self.client.collection("instituciones")
                .where(filter=firestore.FieldFilter(f"{service}_id","==", service_id))
                .limit(1)
                .get()
                )
        record = record[0]
        if not record.exists:
            raise Exception("Invalid service or id")
        
        return record

    def create_record(self, dislu_id, adaptaria_id, secret):
        data = {
            "adaptaria_id": adaptaria_id, 
            "dislu_id": dislu_id, 
            "secret": self.encrypt(secret), 
            "enabled": True
            }
        return self.client.collection("intituciones").document().set(data)


    def generate_key(self):
        hash_seed = hashlib.sha256(self.secret_key.encode()).digest()
        return base64.urlsafe_b64encode(hash_seed)

    def encrypt(self, secret: str) -> str:
        key = self.generate_key()
        f = Fernet(key)
        token = f.encrypt(secret.encode())
        return token.decode()

    def decrypt(self, token: str) -> str:
        key = self.generate_key()
        f = Fernet(key)
        secret = f.decrypt(token.encode())
        return secret.decode()
