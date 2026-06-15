import os
from dotenv import load_dotenv
from pymongo import MongoClient

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

MONGO_URI = os.getenv("MONGO_URI")
CA_FILE = os.getenv("MONGO_CA_FILE")

class _MongoConnection:
    _instance = None
    _obras_col = None

    @classmethod
    def get_obras_col(cls):
        if cls._obras_col is None:
            if CA_FILE:
                cliente = MongoClient(MONGO_URI, tlsCAFile=CA_FILE)
            else:
                cliente = MongoClient(MONGO_URI)
            db = cliente["defaultdb"]
            cls._obras_col = db["obras"]
        return cls._obras_col

obras_col = _MongoConnection.get_obras_col()