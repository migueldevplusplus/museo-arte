import os
import sys
from typing import Optional

from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mongo_service.db_mongo import obras_col
from mongo_service.schemas import ObraResponse, ObraListResponse, EstadisticaGenero

app = FastAPI(
    title="Microservicio MongoDB — Catálogo de Obras",
    description="API REST para el catálogo de obras de arte del Museo",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _serialize_obra(doc: dict) -> dict:
    doc["oid"] = str(doc.pop("_id"))
    return doc


@app.get("/api/obras", response_model=list[ObraListResponse])
def listar_obras(
    genre: Optional[str] = Query(None, description="Filtrar por género"),
    artist: Optional[str] = Query(None, alias="artist", description="Filtrar por nombre del artista"),
    min_price: Optional[float] = Query(None, alias="min_price"),
    max_price: Optional[float] = Query(None, alias="max_price"),
    status: Optional[str] = Query(None, description="AVAILABLE, RESERVED, SOLD"),
    sort: Optional[str] = Query("price", description="price, price_desc, title, title_desc"),
):
    project = {
        "_id": 1, "title": 1, "artist.name": 1, "artist._id": 1,
        "artist.nationality": 1, "artist.biography": 1,
        "genre": 1, "price": 1, "status": 1, "creation_date": 1, "photo": 1
    }

    sort_field = "price"
    sort_dir = 1
    if sort == "price_desc":
        sort_dir = -1
    elif sort == "title":
        sort_field = "title"
    elif sort == "title_desc":
        sort_field = "title"
        sort_dir = -1

    match = {}

    if genre:
        match["genre"] = genre
    if artist:
        match["artist.name"] = artist
    if min_price is not None:
        match.setdefault("price", {})["$gte"] = min_price
    if max_price is not None:
        match.setdefault("price", {})["$lte"] = max_price
    if status:
        match["status"] = status

    try:
        if match:
            pipeline = [
                {"$match": match},
                {"$sort": {sort_field: sort_dir}},
                {"$project": project}
            ]
            obras = [_serialize_obra(doc) for doc in obras_col.aggregate(pipeline)]
        else:
            cursor = obras_col.find({}, project).sort(sort_field, sort_dir)
            obras = [_serialize_obra(doc) for doc in cursor]
        return obras
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/obras/generos", response_model=list[str])
def listar_generos():
    try:
        return sorted(obras_col.distinct("genre"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/obras/artistas", response_model=list[str])
def listar_artistas():
    try:
        return sorted(obras_col.distinct("artist.name"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/obras/estadisticas", response_model=list[EstadisticaGenero])
def estadisticas_por_genero():
    try:
        resultado = obras_col.aggregate([
            {"$group": {
                "_id": "$genre",
                "total_obras": {"$sum": 1},
                "precio_promedio": {"$avg": "$price"}
            }},
            {"$sort": {"total_obras": -1}}
        ])
        return [
            EstadisticaGenero(genre=r["_id"], total_obras=r["total_obras"], precio_promedio=round(r["precio_promedio"], 2))
            for r in resultado
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/obras/{oid}", response_model=ObraResponse)
def detalle_obra(oid: str):
    try:
        obra = obras_col.find_one({"_id": ObjectId(oid)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    if not obra:
        raise HTTPException(status_code=404, detail="Obra no encontrada")

    return _serialize_obra(obra)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mongo_service.main:app", host="127.0.0.1", port=8001, reload=True)
