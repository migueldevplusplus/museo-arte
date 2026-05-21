import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
print("URI cargada:", os.getenv("MONGO_URI"))

MONGO_URI = os.getenv("MONGO_URI")
CA_FILE = os.getenv("MONGO_CA_FILE")

if CA_FILE:
    cliente = MongoClient(MONGO_URI, tlsCAFile=CA_FILE)
else:
    cliente = MongoClient(MONGO_URI)

# Aquí elige la base de datos explícitamente
db = cliente["defaultdb"]   # cámbialo por "catalogo_arte" si es otro
obras_col = db["obras"]

print("✅ Conexión exitosa a MongoDB. Colección:", obras_col)