import random
import string
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from .forms import BuyerRegistrationForm, CodeRecoveryEmailForm, CodeRecoveryQuestionsForm
from .models import BuyerProfile
from museum.models import Membership
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from museum.models import Sale
from django.contrib.auth import authenticate
from django.contrib import messages
from django.core.mail import send_mail
import random
import string
from django.conf import settings

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
                f'Gracias por registrarse. Su código de seguridad para las compras es: {code}',
                settings.DEFAULT_FROM_EMAIL,
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

@login_required
def profile(request):
    user = request.user
    
    # Verificar si el usuario tiene buyer_profile (solo compradores)
    has_profile = hasattr(user, 'buyer_profile')
    
    # Estadísticas de compras (solo si es comprador)
    purchases = Sale.objects.none()
    total_purchases = 0
    total_spent = 0
    membership = None
    
    if has_profile:
        purchases = Sale.objects.filter(buyer=user).select_related('artwork', 'artwork__artist')
        total_purchases = purchases.count()
        total_spent = purchases.aggregate(Sum('total'))['total__sum'] or 0
        
        # Membresía activa (si existe)
        membership = Membership.objects.filter(buyer_profile=user.buyer_profile).first()
    
    context = {
        'user': user,
        'purchases': purchases,
        'total_purchases': total_purchases,
        'total_spent': total_spent,
        'membership': membership,
        'join_date': user.date_joined,
        'has_profile': has_profile,
    }
    return render(request, 'users/profile.html', context)


@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None:
            user.delete()
            messages.success(request, 'Su cuenta ha sido eliminada permanentemente.')
            return redirect('home')
        else:
            messages.error(request, 'Contraseña incorrecta. No se eliminó la cuenta.')
            return redirect('profile')
    
    return render(request, 'users/delete_account_confirm.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None:
            # Eliminar usuario (cascade eliminará BuyerProfile y relaciones)
            user.delete()
            messages.success(request, 'Su cuenta ha sido eliminada permanentemente.')
            return redirect('home')
        else:
            messages.error(request, 'Contraseña incorrecta. No se eliminó la cuenta.')
            return redirect('profile')
    
    return render(request, 'users/delete_account_confirm.html')

@login_required
def change_email(request):
    if request.method == 'POST':
        if 'send_code' in request.POST:
            # Generar y enviar código
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            request.session['email_change_code'] = code
            request.session['new_email'] = request.POST.get('new_email')
            
            send_mail(
                'Código de verificación - Cambio de email',
                f'Su código para cambiar su correo electrónico es: {code}',
                'admin@museum.com',
                [request.user.email],
                fail_silently=False,
            )
            messages.info(request, 'Se envió un código a su email actual.')
            return render(request, 'users/change_email.html', {'step': 'verify'})
        
        elif 'verify_code' in request.POST:
            # Verificar código
            input_code = request.POST.get('code')
            if input_code == request.session.get('email_change_code'):
                new_email = request.session.get('new_email')
                request.user.email = new_email
                request.user.save()
                
                # Limpiar sesión
                del request.session['email_change_code']
                del request.session['new_email']
                
                messages.success(request, 'Correo electrónico actualizado correctamente.')
                return redirect('profile')
            else:
                messages.error(request, 'Código incorrecto.')
    
    return render(request, 'users/change_email.html', {'step': 'request'})


@login_required
def change_password(request):
    if request.method == 'POST':
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        
        # Verificar contraseña actual
        if not request.user.check_password(current):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return redirect('change_password')
        
        # Verificar que nueva y confirmación coincidan
        if new != confirm:
            messages.error(request, 'Las contraseñas nuevas no coinciden.')
            return redirect('change_password')
        
        # Cambiar contraseña
        request.user.set_password(new)
        request.user.save()
        
        messages.success(request, 'Contraseña actualizada correctamente. Vuelve a iniciar sesión.')
        return redirect('login')
    
    return render(request, 'users/change_password.html')
