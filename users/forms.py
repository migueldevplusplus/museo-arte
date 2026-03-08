from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, BuyerProfile

class BuyerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    credit_card_number = forms.CharField(max_length=19, required=True, help_text="XXXX-XXXX-XXXX-XXXX")
    shipping_address = forms.CharField(widget=forms.Textarea, required=True)
    
    security_answer_1 = forms.CharField(max_length=100, required=True, label="¿Cuál es tu color favorito?")
    security_answer_2 = forms.CharField(max_length=100, required=True, label="¿En qué ciudad naciste?")
    security_answer_3 = forms.CharField(max_length=100, required=True, label="¿Cuál es el nombre de tu escuela primaria?")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_buyer = True
        if commit:
            user.save()
            BuyerProfile.objects.create(
                user=user,
                credit_card_number=self.cleaned_data['credit_card_number'],
                shipping_address=self.cleaned_data['shipping_address'],
                security_question_1='q1', # Hardcoded
                security_answer_1=self.cleaned_data['security_answer_1'],
                security_question_2='q2', # Hardcoded
                security_answer_2=self.cleaned_data['security_answer_2'],
                security_question_3='q5', # Hardcoded
                security_answer_3=self.cleaned_data['security_answer_3'],
            )
        return user

class CodeRecoveryEmailForm(forms.Form):
    email = forms.EmailField(required=True, label="Correo Electrónico")

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

