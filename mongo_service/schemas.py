from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class DetallesPintura(BaseModel):
    technique: Optional[str] = None
    support: Optional[str] = None
    height: Optional[float] = None
    width: Optional[float] = None


class DetallesEscultura(BaseModel):
    material: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    width: Optional[float] = None
    depth: Optional[float] = None


class DetallesFotografia(BaseModel):
    photo_type: Optional[str] = None
    camera: Optional[str] = None
    technique: Optional[str] = None
    height: Optional[float] = None
    width: Optional[float] = None


class DetallesCeramica(BaseModel):
    material: Optional[str] = None
    technique: Optional[str] = None
    glaze_type: Optional[str] = None
    height: Optional[float] = None
    width: Optional[float] = None


class DetallesOrfebreria(BaseModel):
    material: Optional[str] = None
    object_type: Optional[str] = None
    weight: Optional[float] = None
    gemstones: Optional[str] = None


class ArtistaInfo(BaseModel):
    _id: Optional[int] = None
    name: Optional[str] = None
    nationality: Optional[str] = None
    biography: Optional[str] = None


class ObraResponse(BaseModel):
    oid: str
    title: str
    artist: ArtistaInfo
    genre: str
    price: float
    creation_date: Optional[str] = None
    photo: Optional[str] = None
    status: str
    detalles_especificos: Optional[dict] = None


class ObraListResponse(BaseModel):
    oid: str
    title: str
    artist: dict
    genre: str
    price: float
    status: str
    creation_date: Optional[str] = None
    photo: Optional[str] = None


class EstadisticaGenero(BaseModel):
    genre: str
    total_obras: int
    precio_promedio: float
