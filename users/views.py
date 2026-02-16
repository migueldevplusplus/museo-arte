import random
import string
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from .forms import BuyerRegistrationForm
from .models import BuyerProfile
from museum.models import Membership

def register(request):
    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Generate random security code
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Update profile with code
            profile = user.buyer_profile
            profile.security_code = code
            profile.save()
            
            # Create Membership (Mock payment)
            Membership.objects.create(buyer_profile=profile)
            
            # Send code via email
            send_mail(
                'Your Security Code',
                f'Thank you for registering. Your security code for purchases is: {code}',
                'admin@museum.com',
                [user.email],
                fail_silently=False,
            )
            
            login(request, user)
            messages.success(request, f'Registration successful! Security code sent to {user.email}')
            return redirect('home')
    else:
        form = BuyerRegistrationForm()
    return render(request, 'users/register.html', {'form': form})
