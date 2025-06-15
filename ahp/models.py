from django.db import models

# Model untuk menyimpan informasi umum perhitungan AHP
class PerhitunganAHP(models.Model):
    lambda_max = models.FloatField()
    CI = models.FloatField()
    CR = models.FloatField()
    lambda_max = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perhitungan AHP - {self.created_at}"

# Model untuk Matriks Perbandingan
class MatriksPerbandingan(models.Model):
    perhitungan = models.ForeignKey(PerhitunganAHP, on_delete=models.CASCADE, related_name='matriks')
    row_kriteria = models.CharField(max_length=100)  # Misal: 'C1', 'C2', dll
    column_kriteria = models.CharField(max_length=100)  # Misal: 'C1', 'C2', dll
    value = models.FloatField()  # Nilai perbandingan antara kriteria

    def __str__(self):
        return f"Perbandingan {self.row_kriteria} vs {self.column_kriteria} - {self.value}"

# Model untuk Matriks Normalisasi
class MatriksNormalisasi(models.Model):
    perhitungan = models.ForeignKey(PerhitunganAHP, on_delete=models.CASCADE, related_name='normalisasi')
    row_kriteria = models.CharField(max_length=100)
    column_kriteria = models.CharField(max_length=100)
    normalized_value = models.FloatField()  # Nilai normalisasi

    def __str__(self):
        return f"Normalisasi {self.row_kriteria} vs {self.column_kriteria} - {self.normalized_value}"

# Model untuk Bobot Kriteria
class BobotKriteria(models.Model):
    perhitungan = models.ForeignKey(PerhitunganAHP, on_delete=models.CASCADE, related_name='bobot')
    kriteria = models.CharField(max_length=100)
    weight = models.FloatField()  # Bobot kriteria
    weighted_sum_matrix = models.FloatField(default=0)  # Jumlah kolom
    eigen_value = models.FloatField(default=0)  # Eigen value untuk kriteria

    def __str__(self):
        return f"Bobot {self.kriteria} - {self.weight}"
