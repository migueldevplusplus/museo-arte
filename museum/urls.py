from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('artist/<int:pk>/', views.artist_detail, name='artist_detail'),
    path('artwork/<int:pk>/reserve/', views.reserve_artwork, name='reserve_artwork'),
    
    # Reports
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/memberships/', views.membership_report, name='membership_report'),
]
