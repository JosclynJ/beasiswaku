from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from user.models import *

import pandas as pd

class Command(BaseCommand):
    help = 'Mengimpor data mahasiswa ke dalam database'

    def handle(self, *args, **kwargs):
        # Memuat data dari file Excel
        df = pd.read_excel('user/management/commands/data_mahasiswa.xlsx')

        for _, row in df.iterrows():
            # Mengambil NIM, Nama, dan membaginya menjadi first name dan last name
            nim = str(row['NIM'])
            name_parts = row['Nama Mahasiswa'].split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])

            # Membuat instance User
            user = User.objects.create_user(username=nim, password=nim, first_name=first_name, last_name=last_name)
            # Menambahkan user ke grup tertentu
            group, created = Group.objects.get_or_create(name='User')  # Gantilah 'Mahasiswa' sesuai grup yang diinginkan
            user.groups.add(group)
            # Membuat instance UserMahasiswa dan menghubungkannya dengan User
            user_mahasiswa = Mahasiswa(
                user=user,
                ipk=row['IPK (Benefit)'],
                penghasilan_orang_tua=row['Penghasilan Orang Tua (Rp) (Cost)'],
                jumlah_tanggungan=row['Jumlah Tanggungan (Benefit)'],
                usia=row['Usia (tahun) (Cost)'],
                is_calculated=False,  # Nilai default
                is_lolos=None,  # Nilai default
                rank=None,  # Nilai default
                total_score=None  # Nilai default
            )
            user_mahasiswa.save()

        self.stdout.write(self.style.SUCCESS('Data berhasil diimpor'))
