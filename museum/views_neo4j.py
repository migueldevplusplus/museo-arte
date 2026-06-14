from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from neo4j_service.db_neo4j import get_driver
from museum.models import Artwork, Artist, Genre

def _get_neo4j_data(query, params=None):
    """Helper: ejecuta una consulta Cypher y retorna lista de dicts."""
    driver = get_driver()
    with driver.session() as session:
        result = session.run(query, **(params or {}))
        return [dict(r) for r in result]


@user_passes_test(lambda u: u.is_staff or u.is_employee)
def dashboard_neo4j(request):
    """Redirige al primer reporte."""
    return redirect('neo4j_recomendaciones')


@user_passes_test(lambda u: u.is_staff or u.is_employee)
def recomendaciones_usuario(request):
    """
    Q1: Recomendar obras del mismo género que compró el usuario,
    excluyendo las ya adquiridas.
    """
    # Obtener lista de compradores desde MySQL
    from users.models import User
    buyers = User.objects.filter(is_buyer=True).order_by('username')

    selected_username = request.GET.get('username', '')
    recomendaciones = []
    total = 0

    if selected_username:
        rows = _get_neo4j_data("""
            MATCH (b:Buyer {username:$u})-[:BOUGHT]->(a:Artwork)
            WITH b, collect(DISTINCT a.genre_name) AS genres
            MATCH (other:Artist)-[:CREATED]->(rec:Artwork)
            WHERE rec.genre_name IN genres
              AND NOT (b)-[:BOUGHT]->(rec)
            RETURN DISTINCT rec.id AS artwork_id, rec.title AS obra,
                   rec.price AS precio, other.name AS artista,
                   rec.genre_name AS genero
            ORDER BY rec.price DESC
        """, {'u': selected_username})
        recomendaciones = rows
        total = len(recomendaciones)

    return render(request, 'museum/neo4j/recomendaciones.html', {
        'buyers': buyers,
        'selected_username': selected_username,
        'recomendaciones': recomendaciones,
        'total': total,
        'active_tab': 'recomendaciones',
    })


@user_passes_test(lambda u: u.is_staff or u.is_employee)
def obras_relacionadas(request):
    """
    Q3: Obras relacionadas por género a una obra específica.
    """
    artworks = Artwork.objects.all().order_by('title')
    selected_artwork_id = request.GET.get('artwork_id', '')
    relacionadas = []
    total = 0
    titulo_base = ''

    if selected_artwork_id:
        try:
            aid = int(selected_artwork_id)
            # Título desde MySQL
            aw = Artwork.objects.filter(id=aid).first()
            if aw:
                titulo_base = aw.title

            rows = _get_neo4j_data("""
                MATCH (aw:Artwork {id:$id})
                MATCH (other:Artist)-[:CREATED]->(related:Artwork {genre_name: aw.genre_name})
                WHERE related.id <> $id
                RETURN DISTINCT related.id AS artwork_id,
                       related.title AS obra, related.price AS precio,
                       other.name AS artista, related.genre_name AS genero
                ORDER BY related.price DESC
            """, {'id': aid})
            relacionadas = rows
            total = len(relacionadas)
        except ValueError:
            pass

    return render(request, 'museum/neo4j/obras_relacionadas.html', {
        'artworks': artworks,
        'selected_artwork_id': selected_artwork_id,
        'titulo_base': titulo_base,
        'relacionadas': relacionadas,
        'total': total,
        'active_tab': 'obras_relacionadas',
    })


@user_passes_test(lambda u: u.is_staff or u.is_employee)
def artistas_similares(request):
    """
    Q4: Artistas similares (comparten género(s)).
    """
    artists = Artist.objects.all().order_by('name')
    selected_artist = request.GET.get('artist_name', '')
    similares = []
    total = 0

    if selected_artist:
        rows = _get_neo4j_data("""
            MATCH (a1:Artist {name:$name})-[:WORKS_IN]->(g:Genre)
            MATCH (g)<-[:WORKS_IN]-(a2:Artist)
            WHERE a1 <> a2
            RETURN DISTINCT a2.name AS artista,
                   collect(g.name) AS generos_compartidos
            ORDER BY a2.name
        """, {'name': selected_artist})
        similares = rows
        total = len(similares)

    return render(request, 'museum/neo4j/artistas_similares.html', {
        'artists': artists,
        'selected_artist': selected_artist,
        'similares': similares,
        'total': total,
        'active_tab': 'artistas_similares',
    })


@user_passes_test(lambda u: u.is_staff or u.is_employee)
def compradores_por_genero(request):
    """
    Q5: Compradores que han adquirido obras de un género específico.
    """
    genres = Genre.objects.all().order_by('name')
    selected_genre = request.GET.get('genre_name', '')
    compradores = []
    total = 0

    if selected_genre:
        rows = _get_neo4j_data("""
            MATCH (b:Buyer)-[:BOUGHT]->(a:Artwork)
            WHERE a.genre_name = $genre
            RETURN b.username AS comprador, b.email AS email,
                   count(a) AS obras_compradas,
                   collect(a.title) AS titulos
            ORDER BY obras_compradas DESC
        """, {'genre': selected_genre})
        compradores = rows
        total = len(compradores)

    return render(request, 'museum/neo4j/compradores_por_genero.html', {
        'genres': genres,
        'selected_genre': selected_genre,
        'compradores': compradores,
        'total': total,
        'active_tab': 'compradores_genero',
    })


@user_passes_test(lambda u: u.is_staff or u.is_employee)
def obras_mismo_artista(request):
    """
    Q2: Obras del mismo artista que el usuario ya compró.
    """
    from users.models import User
    buyers = User.objects.filter(is_buyer=True).order_by('username')

    selected_username = request.GET.get('username', '')
    obras = []
    total = 0

    if selected_username:
        rows = _get_neo4j_data("""
            MATCH (b:Buyer {username:$u})-[:BOUGHT]->(:Artwork)
            MATCH (a:Artist)-[:CREATED]->(rec:Artwork)
            WHERE (a)-[:CREATED]->(:Artwork)<-[:BOUGHT]-(b)
              AND NOT (b)-[:BOUGHT]->(rec)
            RETURN DISTINCT rec.id AS artwork_id, rec.title AS obra,
                   rec.price AS precio, a.name AS artista
            ORDER BY rec.price DESC
        """, {'u': selected_username})
        obras = rows
        total = len(obras)

    return render(request, 'museum/neo4j/mismo_artista.html', {
        'buyers': buyers,
        'selected_username': selected_username,
        'obras': obras,
        'total': total,
        'active_tab': 'mismo_artista',
    })
