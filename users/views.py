import random
import string
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from .forms import BuyerRegistrationForm, CodeRecoveryEmailForm, CodeRecoveryQuestionsForm
from .models import BuyerProfile
from museum.models import Membership

User = get_user_model()

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
                'Tu código de seguridad',
                f'Gracias por registrarte. Tu código de seguridad para las compras es: {code}',
                'admin@museum.com',
                [user.email],
                fail_silently=False,
            )
            
            login(request, user)
            messages.success(request, f'Registro exitoso! Código de seguridad enviado a {user.email}')
            return redirect('home')
    else:
        form = BuyerRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def recover_code_email(request):
    if request.method == 'POST':
        form = CodeRecoveryEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email, is_buyer=True).first()
            if user and hasattr(user, 'buyer_profile'):
                request.session['recovery_user_id'] = user.id
                return redirect('recover_code_questions')
            else:
                messages.error(request, 'No se encontró un perfil de comprador con ese correo.')
    else:
        form = CodeRecoveryEmailForm()
    return render(request, 'users/recover_code_email.html', {'form': form})

def recover_code_questions(request):
    user_id = request.session.get('recovery_user_id')
    if not user_id:
        return redirect('recover_code_email')
        
    user = get_object_or_404(User, id=user_id)
    profile = user.buyer_profile
    
    if request.method == 'POST':
        form = CodeRecoveryQuestionsForm(request.POST, profile=profile)
        if form.is_valid():
            ans1 = form.cleaned_data['security_answer_1']
            ans2 = form.cleaned_data['security_answer_2']
            ans3 = form.cleaned_data['security_answer_3']
            
            # Simple case-insensitive comparison
            if (ans1.strip().lower() == profile.security_answer_1.strip().lower() and
                ans2.strip().lower() == profile.security_answer_2.strip().lower() and
                ans3.strip().lower() == profile.security_answer_3.strip().lower()):
                
                # Generate new code
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                profile.security_code = code
                profile.save()
                
                # Send email
                send_mail(
                    'Su Nuevo Código de Seguridad',
                    f'Su nuevo código de seguridad para compras es: {code}',
                    'admin@museum.com',
                    [user.email],
                    fail_silently=False,
                )
                
                # Clear session
                if 'recovery_user_id' in request.session:
                    del request.session['recovery_user_id']
                    
                return redirect('recover_code_success')
            else:
                messages.error(request, 'Una o más respuestas son incorrectas.')
    else:
        form = CodeRecoveryQuestionsForm(profile=profile)
        
    return render(request, 'users/recover_code_questions.html', {'form': form})

def recover_code_success(request):
    return render(request, 'users/recover_code_success.html')
