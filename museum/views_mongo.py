from django.shortcuts import render
from django.conf import settings
import httpx

API_URL = getattr(settings, "MONGO_API_URL", "http://localhost:8001")


def mongo_queries(request):
    try:
        with httpx.Client() as client:
            generos_resp = client.get(f"{API_URL}/api/obras/generos", timeout=10)
            artistas_resp = client.get(f"{API_URL}/api/obras/artistas", timeout=10)
        generos_resp.raise_for_status()
        artistas_resp.raise_for_status()
        genres = generos_resp.json()
        artist_names = artistas_resp.json()
    except Exception as e:
        return render(request, "museum/mongo/queries.html", {"error": str(e)})

    params = {}
    genre = request.GET.get("genre")
    artist = request.GET.get("artist")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    status = request.GET.get("status")
    sort_by = request.GET.get("sort", "price")

    if genre:
        params["genre"] = genre
    if artist:
        params["artist"] = artist
    if min_price:
        params["min_price"] = min_price
    if max_price:
        params["max_price"] = max_price
    if status:
        params["status"] = status
    if sort_by:
        params["sort"] = sort_by

    try:
        with httpx.Client() as client:
            obras_resp = client.get(f"{API_URL}/api/obras", params=params, timeout=10)
        obras_resp.raise_for_status()
        obras = obras_resp.json()
    except Exception as e:
        return render(request, "museum/mongo/queries.html", {"error": str(e)})

    return render(request, "museum/mongo/queries.html", {
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
        with httpx.Client() as client:
            resp = client.get(f"{API_URL}/api/obras/{oid}", timeout=10)
        resp.raise_for_status()
        obra = resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return render(request, "museum/mongo/artwork_detail.html", {"error": "Obra no encontrada"})
        return render(request, "museum/mongo/artwork_detail.html", {"error": str(e)})
    except Exception as e:
        return render(request, "museum/mongo/artwork_detail.html", {"error": str(e)})

    return render(request, "museum/mongo/artwork_detail.html", {"obra": obra})
