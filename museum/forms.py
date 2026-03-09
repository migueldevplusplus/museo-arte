from django import forms
from .models import Sale, Artwork

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['artwork', 'buyer', 'payment_method', 'shipping_address', 'subtotal']
        widgets = {
            'artwork': forms.Select(attrs={'class': 'form-select'}),
            'buyer': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit artwork selection to those that are not sold. 
        # (Admins might want to invoice available or reserved artworks).
        self.fields['artwork'].queryset = Artwork.objects.exclude(status='SOLD')
