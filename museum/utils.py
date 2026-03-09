from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import Reservation

def cleanup_expired_reservations():
    """
    Finds reservations that are older than RESERVATION_TIMEOUT_HOURS
    (default 24 hours), deletes them, and resets the corresponding
    artwork's status to 'AVAILABLE'.
    """
    timeout_hours = getattr(settings, 'RESERVATION_TIMEOUT_HOURS', 24)
    expiration_threshold = timezone.now() - timedelta(hours=timeout_hours)
    
    # Find expired reservations
    expired_reservations = Reservation.objects.filter(date__lt=expiration_threshold)
    
    for reservation in expired_reservations:
        artwork = reservation.artwork
        # Reset artwork status
        artwork.status = 'AVAILABLE'
        artwork.save()
        # Delete the reservation
        reservation.delete()
