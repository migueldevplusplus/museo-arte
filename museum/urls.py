from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('artist/<int:pk>/', views.artist_detail, name='artist_detail'),
    path('artwork/<int:pk>/reserve/', views.reserve_artwork, name='reserve_artwork'),
    
    # Sales & Reservations
    path('sales/process/', views.process_sale, name='process_sale'),
    path('sales/invoice/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('reservations/manage/', views.manage_reservations, name='manage_reservations'),
    path('reservations/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    
    # Reports
    path('reports/sold-artworks/', views.sold_artworks_report, name='sold_artworks_report'),
    path('reports/billing-summary/', views.billing_summary_report, name='billing_summary_report'),
    path('reports/memberships/', views.membership_report, name='membership_report'),

    # CRUD para administradores
    path('admin-panel/genres/', views.GenreListView.as_view(), name='genre_list'),
    path('admin-panel/genres/create/', views.GenreCreateView.as_view(), name='genre_create'),
    path('admin-panel/genres/<int:pk>/update/', views.GenreUpdateView.as_view(), name='genre_update'),
    path('admin-panel/genres/<int:pk>/delete/', views.GenreDeleteView.as_view(), name='genre_delete'),

    path('admin-panel/artists/', views.ArtistListView.as_view(), name='artist_list'),
    path('admin-panel/artists/create/', views.ArtistCreateView.as_view(), name='artist_create'),
    path('admin-panel/artists/<int:pk>/update/', views.ArtistUpdateView.as_view(), name='artist_update'),
    path('admin-panel/artists/<int:pk>/delete/', views.ArtistDeleteView.as_view(), name='artist_delete'),

    path('admin-panel/artworks/', views.ArtworkListView.as_view(), name='artwork_list'),
    path('admin-panel/artworks/create/', views.ArtworkCreateView.as_view(), name='artwork_create'),
    path('admin-panel/artworks/<int:pk>/update/', views.ArtworkUpdateView.as_view(), name='artwork_update'),
    path('admin-panel/artworks/<int:pk>/delete/', views.ArtworkDeleteView.as_view(), name='artwork_delete'),
]

