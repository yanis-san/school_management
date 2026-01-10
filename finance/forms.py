from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'transaction_id', 'receipt']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Montant en DA'}),
            'method': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'transaction_id': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Numéro de chèque (Optionnel)'}),
            'receipt': forms.FileInput(attrs={'class': 'hidden', 'accept': '.pdf,.jpg,.jpeg,.png,.webp'}),
        }
        labels = {
            'amount': 'Montant (DA)',
            'method': 'Mode de paiement',
            'transaction_id': 'Référence / Note',
            'receipt': 'Reçu / Justificatif',
        }