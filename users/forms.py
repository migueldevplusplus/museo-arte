from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, BuyerProfile

class BuyerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    credit_card_number = forms.CharField(max_length=19, required=True, help_text="XXXX-XXXX-XXXX-XXXX")
    shipping_address = forms.CharField(widget=forms.Textarea, required=True)

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
                shipping_address=self.cleaned_data['shipping_address']
            )
        return user
