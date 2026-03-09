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
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/memberships/', views.membership_report, name='membership_report'),
]
