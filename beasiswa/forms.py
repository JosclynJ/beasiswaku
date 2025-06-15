from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UbahPasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password Sekarang",
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password Baru",
        required=True,
        # min_length=8  # Menetapkan minimal panjang password baru
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Konfirmasi Password Baru",
        required=True
    )