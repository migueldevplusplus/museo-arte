from mongo_service.db_mongo import obras_col

print("=== TODOS LOS DOCUMENTOS DE LA COLECCIÓN 'obras' ===\n")

for doc in obras_col.find():          # .find() sin filtros = SELECT *
    print(doc)
    print("-" * 50)                   # separador entre documentos

print(f"\nTotal de documentos: {obras_col.count_documents({})}")