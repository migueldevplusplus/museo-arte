from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, F
from django.core.mail import send_mail
from .models import Artwork, Artist, Genre, Sale, Membership, Reservation
from users.models import BuyerProfile
from django.utils import timezone
import datetime

def home(request):
    featured_artworks = Artwork.objects.filter(status='AVAILABLE').order_by('-creation_date')[:3]
    return render(request, 'museum/home.html', {'featured_artworks': featured_artworks})

def catalog(request):
    artworks = Artwork.objects.all()
    
    # Filters
    genre_id = request.GET.get('genre')
    artist_id = request.GET.get('artist')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'price') # Default sort by price asc

    if genre_id:
        artworks = artworks.filter(genre_id=genre_id)
    if artist_id:
        artworks = artworks.filter(artist_id=artist_id)
    if min_price:
        artworks = artworks.filter(price__gte=min_price)
    if max_price:
        artworks = artworks.filter(price__lte=max_price)
        
    if sort_by == 'price_desc':
        artworks = artworks.order_by('-price')
    else:
        artworks = artworks.order_by('price')

    genres = Genre.objects.all()
    artists = Artist.objects.all()

    # Convert to int for template comparison
    try:
        selected_genre_id = int(genre_id) if genre_id else None
    except ValueError:
        selected_genre_id = None
        
    try:
        selected_artist_id = int(artist_id) if artist_id else None
    except ValueError:
        selected_artist_id = None

    return render(request, 'museum/catalog.html', {
        'artworks': artworks,
        'genres': genres,
        'artists': artists,
        'selected_genre_id': selected_genre_id,
        'selected_artist_id': selected_artist_id,
    })

def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    # Resolve to the specialized child instance (Painting, Sculpture, etc.)
    specific = artwork.get_specific_instance()
    detail_fields = specific.get_detail_fields()
    return render(request, 'museum/artwork_detail.html', {
        'artwork': artwork,
        'detail_fields': detail_fields,
    })

def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    return render(request, 'museum/artist_detail.html', {'artist': artist})

@login_required
def reserve_artwork(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    
    # Verificar si la obra está disponible
    if artwork.status != 'AVAILABLE':
        messages.error(request, 'This artwork is not available.')
        return redirect('catalog')
        
    # Verificar si el usuario es comprador
    if not hasattr(request.user, 'buyer_profile'):
        messages.error(request, 'You must be a registered buyer to purchase.')
        return redirect('register')

    # VERIFICAR SI EL USUARIO YA RESERVÓ ESTA OBRA
    existing_reservation = Reservation.objects.filter(
        artwork=artwork, 
        user=request.user
    ).exists()
    
    if existing_reservation:
        messages.warning(request, 'You have already reserved this artwork.')
        return redirect('artwork_detail', pk=artwork.pk)
    
    if request.method == 'POST':
        code = request.POST.get('security_code')
        if code == request.user.buyer_profile.security_code:
            
            # DOBLE VERIFICACIÓN: Recargar desde BD por si acaso
            artwork.refresh_from_db()
            
            if artwork.status != 'AVAILABLE':
                messages.error(request, 'This artwork was just reserved by someone else.')
                return redirect('catalog')
            
            # CREAR LA RESERVA EN BD
            reservation = Reservation.objects.create(
                artwork=artwork,
                user=request.user,
                security_code_used=code
            )
            
            # Cambiar status de la obra
            artwork.status = 'RESERVED'
            artwork.save()
            
            messages.success(request, f'Artwork "{artwork.title}" reserved successfully!')
            return redirect('artwork_detail', pk=artwork.pk)
        else:
            messages.error(request, 'Invalid security code.')
            
    return render(request, 'museum/reserve_artwork.html', {'artwork': artwork})

# Admin Reports
@user_passes_test(lambda u: u.is_staff or u.is_employee)
def sales_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    sales = Sale.objects.all()
    
    if start_date and end_date:
        sales = sales.filter(date__date__range=[start_date, end_date])

    total_revenue = sales.aggregate(Sum('total'))['total__sum'] or 0
    total_commission = sales.aggregate(Sum('commission'))['commission__sum'] or 0
    
    return render(request, 'museum/reports/sales_report.html', {
        'sales': sales,
        'total_revenue': total_revenue,
        'total_commission': total_commission
    })

@user_passes_test(lambda u: u.is_staff or u.is_employee)
def membership_report(request):
    memberships = Membership.objects.all()
    # Add date filtering if needed
    
    total_collected = memberships.aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'museum/reports/membership_report.html', {
        'memberships': memberships,
        'total_collected': total_collected
    })
