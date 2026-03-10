from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import User, BuyerProfile

class BuyerRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingrese un correo electrónico válido (ej: nombre@dominio.com).'
        }
    )
    
    credit_card_number = forms.CharField(
        max_length=19, 
        required=True, 
        help_text="XXXX-XXXX-XXXX-XXXX",
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{4}-\d{4}-\d{4}$',
                message='El número de tarjeta debe tener el formato XXXX-XXXX-XXXX-XXXX (16 dígitos separados por guiones).',
                code='invalid_credit_card'
            )
        ],
        widget=forms.TextInput(attrs={
            'pattern': r'\d{4}-\d{4}-\d{4}-\d{4}',
            'placeholder': 'XXXX-XXXX-XXXX-XXXX',
            'title': 'Formato: XXXX-XXXX-XXXX-XXXX'
        }),
        error_messages={
            'required': 'El número de tarjeta de crédito es obligatorio.',
            'max_length': 'El número de tarjeta debe tener 16 dígitos.'
        }
    )
    
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=True,
        error_messages={
            'required': 'La dirección de envío es obligatoria.'
        }
    )
    
    security_answer_1 = forms.CharField(
        max_length=100, 
        required=True, 
        label="¿Cuál es tu color favorito?",
        error_messages={
            'required': 'La respuesta a esta pregunta es obligatoria.'
        }
    )
    
    security_answer_2 = forms.CharField(
        max_length=100, 
        required=True, 
        label="¿En qué ciudad naciste?",
        error_messages={
            'required': 'La respuesta a esta pregunta es obligatoria.'
        }
    )
    
    security_answer_3 = forms.CharField(
        max_length=100, 
        required=True, 
        label="¿Cuál es el nombre de tu escuela primaria?",
        error_messages={
            'required': 'La respuesta a esta pregunta es obligatoria.'
        }
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Mensajes personalizados para username
        self.fields['username'].error_messages = {
            'required': 'El nombre de usuario es obligatorio.',
            'unique': 'Este nombre de usuario ya está en uso. Por favor, elija otro.',
            'max_length': 'El nombre de usuario no puede tener más de 150 caracteres.',
        }
        
        # Mensajes personalizados para first_name
        self.fields['first_name'].required = False
        self.fields['first_name'].error_messages = {
            'max_length': 'El nombre no puede tener más de 30 caracteres.',
        }
        
        # Mensajes personalizados para last_name
        self.fields['last_name'].required = False
        self.fields['last_name'].error_messages = {
            'max_length': 'El apellido no puede tener más de 30 caracteres.',
        }
        
        # Mensajes personalizados para password1
        self.fields['password1'].error_messages = {
            'required': 'La contraseña es obligatoria.',
            'password_too_short': 'La contraseña debe tener al menos 8 caracteres.',
            'password_too_common': 'La contraseña es demasiado común. Elija una más segura.',
            'password_entirely_numeric': 'La contraseña no puede ser completamente numérica.',
        }
        
        self.fields['password2'].error_messages = {
            'required': 'Por favor, confirme su contraseña.',
            'password_mismatch': 'Las contraseñas no coinciden. Verifique que sean iguales.',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_buyer = True
        if commit:
            user.save()
            BuyerProfile.objects.create(
                user=user,
                credit_card_number=self.cleaned_data['credit_card_number'],
                shipping_address=self.cleaned_data['shipping_address'],
                security_question_1='q1',
                security_answer_1=self.cleaned_data['security_answer_1'],
                security_question_2='q2',
                security_answer_2=self.cleaned_data['security_answer_2'],
                security_question_3='q5',
                security_answer_3=self.cleaned_data['security_answer_3'],
            )
        return user


class CodeRecoveryEmailForm(forms.Form):
    email = forms.EmailField(required=True, label="Correo electrónico")

class CodeRecoveryQuestionsForm(forms.Form):
    security_answer_1 = forms.CharField(max_length=100, required=True, label="Respuesta 1")
    security_answer_2 = forms.CharField(max_length=100, required=True, label="Respuesta 2")
    security_answer_3 = forms.CharField(max_length=100, required=True, label="Respuesta 3")

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        if profile:
            questions_dict = dict(BuyerProfile.SECURITY_QUESTIONS)
            self.fields['security_answer_1'].label = questions_dict.get(profile.security_question_1, "¿Cuál es tu color favorito?")
            self.fields['security_answer_2'].label = questions_dict.get(profile.security_question_2, "¿En qué ciudad naciste?")
            self.fields['security_answer_3'].label = questions_dict.get(profile.security_question_3, "¿Cuál es el nombre de tu escuela primaria?")