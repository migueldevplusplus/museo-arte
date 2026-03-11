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
        error_messages = {
            'artwork': {
                'unique': "Esta obra ya tiene una factura o venta oficial registrada en el sistema. Debes eliminar la venta anterior antes de volver a facturarla."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limitar la selección a obras que no estén vendidas.
        self.fields['artwork'].queryset = Artwork.objects.exclude(status='SOLD')
