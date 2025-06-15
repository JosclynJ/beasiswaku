from django import forms
from user.models import Mahasiswa
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class MahasiswaForm(forms.ModelForm):
    class Meta:
        model = Mahasiswa
        fields = ['ipk', 'penghasilan_orang_tua', 'jumlah_tanggungan', 'usia']
        widgets = {
            'ipk': forms.NumberInput(attrs={'class': 'form-control'}),
            'penghasilan_orang_tua': forms.NumberInput(attrs={'class': 'form-control'}),
            'jumlah_tanggungan': forms.NumberInput(attrs={'class': 'form-control'}),
            'usia': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    # Validasi IPK
    def clean_ipk(self):
        ipk = self.cleaned_data.get('ipk')
        if ipk < 3.00 or ipk > 4.00:
            raise ValidationError("IPK harus antara 3.00 dan 4.00")
        return ipk

    # Validasi Penghasilan Orang Tua
    def clean_penghasilan_orang_tua(self):
        penghasilan = self.cleaned_data.get('penghasilan_orang_tua')
        if penghasilan < 1500000 or penghasilan > 6000000:
            raise ValidationError("Penghasilan orang tua harus antara Rp 1.500.000 dan Rp 6.000.000")
        return penghasilan

    # Validasi Jumlah Tanggungan
    def clean_jumlah_tanggungan(self):
        tanggungan = self.cleaned_data.get('jumlah_tanggungan')
        if tanggungan < 1 or tanggungan > 6:
            raise ValidationError("Jumlah tanggungan harus antara 1 dan 6")
        return tanggungan

    # Validasi Usia
    def clean_usia(self):
        usia = self.cleaned_data.get('usia')
        if usia < 18 or usia > 30:
            raise ValidationError("Usia harus antara 18 dan 30 tahun")
        return usia

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []