from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from decimal import Decimal
from cassandra_service.db_cassandra import get_session
from museum.models import Artwork

# Restringir acceso a administradores y empleados
@user_passes_test(lambda u: u.is_staff or u.is_employee)
def dashboard_home(request):
    """Redirige al primer reporte por defecto o muestra landing."""
    return redirect('reporte_ventas_mes')

@user_passes_test(lambda u: u.is_staff or u.is_employee)
def reporte_ventas_mes(request):
    """
    Q1: Facturación del mes y año.
    Partiton Key: (year, month)
    """
    now = timezone.now()
    year = request.GET.get('year', str(now.year))
    month = request.GET.get('month', str(now.month))

    try:
        year_int = int(year)
        month_int = int(month)
    except ValueError:
        year_int = now.year
        month_int = now.month

    session = get_session()
    
    # Query Cassandra
    query = "SELECT * FROM ventas_por_mes WHERE year = %s AND month = %s"
    rows = session.execute(query, (year_int, month_int))
    sales = list(rows)

    # Calcular totales
    total_subtotal = Decimal('0.00')
    total_iva = Decimal('0.00')
    total_commission = Decimal('0.00')
    total_facturado = Decimal('0.00')

    for r in sales:
        total_subtotal += r.subtotal or Decimal('0.00')
        total_iva += r.iva or Decimal('0.00')
        total_commission += r.commission or Decimal('0.00')
        total_facturado += r.total or Decimal('0.00')

    context = {
        'sales': sales,
        'year': year_int,
        'month': month_int,
        'total_subtotal': total_subtotal,
        'total_iva': total_iva,
        'total_commission': total_commission,
        'total_facturado': total_facturado,
        'years_range': range(now.year - 5, now.year + 2),
        'months_range': range(1, 13),
        'active_tab': 'ventas_mes'
    }
    return render(request, 'museum/cassandra/ventas_mes.html', context)

@user_passes_test(lambda u: u.is_staff or u.is_employee)
def reporte_ventas_artista(request):
    """
    Q3: Ventas del artista específico.
    Partition Key: (artist_name)
    """
    session = get_session()
    
    # Obtener artistas de Cassandra para el filtro de forma dinámica
    artists_rows = session.execute("SELECT DISTINCT artist_name FROM ventas_por_artista")
    artists = sorted([r.artist_name for r in artists_rows if r.artist_name])

    selected_artist = request.GET.get('artist_name', '')
    sales = []
    total_sales = 0
    total_facturado = Decimal('0.00')
    total_commission = Decimal('0.00')

    if selected_artist:
        query = "SELECT * FROM ventas_por_artista WHERE artist_name = %s"
        rows = session.execute(query, (selected_artist,))
        sales = list(rows)
        total_sales = len(sales)
        for r in sales:
            total_facturado += r.total or Decimal('0.00')
            total_commission += r.commission or Decimal('0.00')

    context = {
        'artists': artists,
        'selected_artist': selected_artist,
        'sales': sales,
        'total_sales': total_sales,
        'total_facturado': total_facturado,
        'total_commission': total_commission,
        'active_tab': 'ventas_artista'
    }
    return render(request, 'museum/cassandra/ventas_artista.html', context)

@user_passes_test(lambda u: u.is_staff or u.is_employee)
def reporte_ventas_genero(request):
    """
    Q4: Ventas del género específico.
    Partition Key: (genre_name)
    """
    session = get_session()
    
    # Obtener géneros de Cassandra de forma dinámica
    genres_rows = session.execute("SELECT DISTINCT genre_name FROM ventas_por_genero")
    genres = sorted([r.genre_name for r in genres_rows if r.genre_name])

    selected_genre = request.GET.get('genre_name', '')
    sales = []
    total_sales = 0
    total_facturado = Decimal('0.00')

    if selected_genre:
        query = "SELECT * FROM ventas_por_genero WHERE genre_name = %s"
        rows = session.execute(query, (selected_genre,))
        sales = list(rows)
        total_sales = len(sales)
        for r in sales:
            total_facturado += r.total or Decimal('0.00')

    context = {
        'genres': genres,
        'selected_genre': selected_genre,
        'sales': sales,
        'total_sales': total_sales,
        'total_facturado': total_facturado,
        'active_tab': 'ventas_genero'
    }
    return render(request, 'museum/cassandra/ventas_genero.html', context)

@user_passes_test(lambda u: u.is_staff or u.is_employee)
def reporte_bitacora_eventos(request):
    """
    Q7: Bitácora de eventos por tipo y mes.
    Partition Key: (event_year, event_month, event_type)
    """
    now = timezone.now()
    year = request.GET.get('year', str(now.year))
    month = request.GET.get('month', str(now.month))
    event_type = request.GET.get('event_type', 'VENTA')

    try:
        year_int = int(year)
        month_int = int(month)
    except ValueError:
        year_int = now.year
        month_int = now.month

    session = get_session()
    
    # Query Cassandra
    query = """
        SELECT * FROM bitacora_eventos 
        WHERE event_year = %s AND event_month = %s AND event_type = %s
    """
    rows = session.execute(query, (year_int, month_int, event_type))
    events = list(rows)

    event_types = ['VENTA', 'RESERVA', 'CANCELACION', 'CAMBIO_ESTATUS', 'REGISTRO_USUARIO', 'MEMBRESIA']

    context = {
        'events': events,
        'year': year_int,
        'month': month_int,
        'event_type': event_type,
        'event_types': event_types,
        'years_range': range(now.year - 5, now.year + 2),
        'months_range': range(1, 13),
        'active_tab': 'bitacora'
    }
    return render(request, 'museum/cassandra/bitacora_eventos.html', context)

@user_passes_test(lambda u: u.is_staff or u.is_employee)
def reporte_historial_obra(request):
    """
    Q9: Historial completo de cambios de estatus de una obra.
    Partition Key: (artwork_id)
    """
    # Obtener lista de obras desde MySQL para facilitar la búsqueda / selección
    artworks = Artwork.objects.all().order_by('title')

    selected_artwork_id = request.GET.get('artwork_id', '')
    history = []
    artwork_title = ""

    if selected_artwork_id:
        try:
            artwork_id_int = int(selected_artwork_id)
            session = get_session()
            query = "SELECT * FROM historial_estatus_obra WHERE artwork_id = %s"
            rows = session.execute(query, (artwork_id_int,))
            history = list(rows)
            
            # Buscar el título en MySQL si existe, sino tomarlo del primer registro del historial
            db_artwork = Artwork.objects.filter(id=artwork_id_int).first()
            if db_artwork:
                artwork_title = db_artwork.title
            elif history:
                artwork_title = history[0].artwork_title
        except ValueError:
            pass

    context = {
        'artworks': artworks,
        'selected_artwork_id': selected_artwork_id,
        'artwork_title': artwork_title,
        'history': history,
        'active_tab': 'historial_obra'
    }
    return render(request, 'museum/cassandra/historial_obra.html', context)
