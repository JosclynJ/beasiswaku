from django.db import models
from django.contrib.auth.models import User

class Mahasiswa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mahasiswa', null=True, blank=True)  # Relasi dengan User
    ipk = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # IPK
    penghasilan_orang_tua = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)  # Penghasilan Orang Tua
    jumlah_tanggungan = models.IntegerField(null=True, blank=True)  # Jumlah Tanggungan
    usia = models.IntegerField(null=True, blank=True)  # Usia
    is_calculated = models.BooleanField(default=False)
    is_lolos = models.BooleanField(null=True, default=None)
    rank = models.IntegerField(null=True, blank=True) 
    total_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.user.username  # Menampilkan username (NIM) sebagai representasi mahasiswa
