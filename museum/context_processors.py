from .models import Reservation

def pending_reservations(request):
    if request.user.is_authenticated and (request.user.is_staff or getattr(request.user, 'is_employee', False)):
        has_pending = Reservation.objects.filter(artwork__status='RESERVED').exists()
        return {'has_pending_reservations': has_pending}
    return {'has_pending_reservations': False}
