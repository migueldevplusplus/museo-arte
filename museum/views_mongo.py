from django.shortcuts import render
from bson import ObjectId
from mongo_service.db_mongo import obras_col


def mongo_queries(request):
    try:
        genres = sorted(obras_col.distinct("genre"))
        artist_names = sorted(obras_col.distinct("artist.name"))
    except Exception as e:
        return render(request, 'museum/mongo/queries.html', {"error": str(e)})

    pipeline = []
    match = {}

    genre = request.GET.get("genre")
    artist = request.GET.get("artist")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    status = request.GET.get("status")
    sort_by = request.GET.get("sort", "price")

    if genre:
        match["genre"] = genre
    if artist:
        match["artist.name"] = artist
    if min_price:
        match.setdefault("price", {})["$gte"] = float(min_price)
    if max_price:
        match.setdefault("price", {})["$lte"] = float(max_price)
    if status:
        match["status"] = status

    if match:
        pipeline.append({"$match": match})

    sort_field = "price"
    sort_dir = 1
    if sort_by == "price_desc":
        sort_dir = -1
    elif sort_by == "title":
        sort_field = "title"
    elif sort_by == "title_desc":
        sort_field = "title"
        sort_dir = -1

    pipeline.append({"$sort": {sort_field: sort_dir}})
    pipeline.append({"$project": {
        "_id": 1, "title": 1, "artist.name": 1, "genre": 1, "price": 1, "status": 1, "creation_date": 1, "photo": 1
    }})

    try:
        obras = list(obras_col.aggregate(pipeline))
        for obra in obras:
            obra["oid"] = str(obra.pop("_id"))
    except Exception as e:
        return render(request, 'museum/mongo/queries.html', {"error": str(e)})

    return render(request, 'museum/mongo/queries.html', {
        "obras": obras,
        "genres": genres,
        "artist_names": artist_names,
        "selected_genre": genre or "",
        "selected_artist": artist or "",
        "selected_status": status or "",
        "selected_sort": sort_by,
    })


def mongo_artwork_detail(request, oid):
    try:
        obra = obras_col.find_one({"_id": ObjectId(oid)})
    except Exception as e:
        return render(request, 'museum/mongo/artwork_detail.html', {"error": f"Obra no encontrada: {e}"})

    if not obra:
        return render(request, 'museum/mongo/artwork_detail.html', {"error": "Obra no encontrada"})

    return render(request, 'museum/mongo/artwork_detail.html', {"obra": obra})
