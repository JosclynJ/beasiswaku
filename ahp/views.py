import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from fractions import Fraction  # Import modul Fraction
from django.contrib import  messages
from .models import *
from .forms import *
from user.forms import *
from user.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse


def in_admin(user):
    get_user = user.groups.filter(name='Admin').count()
    if get_user > 0:
        return False
    else:
        return True

def ahp(request):
    if not request.user.is_authenticated:
        return redirect('/')

    template_name = "dashboard/superadmin/ahp.html"
    
    kriteria = {
        'C1': '(C1) IPK',
        'C2': '(C2) Penghasilan',
        'C3': '(C3) Tanggungan',
        'C4': '(C4) Usia'
    }

    def convert_to_fraction(value):
        try:
            if '/' in value:
                return Fraction(value)
            return Fraction(float(value)).limit_denominator()
        except ValueError:
            return Fraction(0)

    def calculate_eigen_value(matrix, weights, perhitungan):
        weighted_sum_matrix = np.dot(matrix, weights)
        eigen_values = weighted_sum_matrix / weights
        return weighted_sum_matrix, eigen_values

    if request.method == 'POST':
        try:
            group_1_value = convert_to_fraction(request.POST.get('group_1', '0'))
            group_2_value = convert_to_fraction(request.POST.get('group_2', '0'))
            group_3_value = convert_to_fraction(request.POST.get('group_3', '0'))
            group_4_value = convert_to_fraction(request.POST.get('group_4', '0'))
            group_5_value = convert_to_fraction(request.POST.get('group_5', '0'))
            group_6_value = convert_to_fraction(request.POST.get('group_6', '0'))
        except ValueError as e:
            print(f"Error converting to float: {e}")

        matrix = [
            [1, group_1_value, group_2_value, group_3_value],
            [1 / group_1_value if group_1_value != 0 else 0, 1, group_4_value, group_5_value],
            [1 / group_2_value if group_2_value != 0 else 0, 1 / group_4_value if group_4_value != 0 else 0, 1, group_6_value],
            [1 / group_3_value if group_3_value != 0 else 0, 1 / group_5_value if group_5_value != 0 else 0, 1 / group_6_value if group_6_value != 0 else 0, 1]
        ]

        column_sums = [sum(row[i] for row in matrix) for i in range(len(matrix[0]))]

        normalized_matrix = []
        for row in matrix:
            normalized_row = [float(row[i]) / float(column_sums[i]) for i in range(len(row))]
            normalized_matrix.append(normalized_row)

        weights = [sum(normalized_matrix[i]) / len(normalized_matrix[i]) for i in range(len(normalized_matrix))]

        weighted_sum_matrix, eigen_values = calculate_eigen_value(matrix, weights, None)

        lambda_max = np.mean(eigen_values)
        n = len(matrix)
        CI = (lambda_max - n) / (n - 1)
        RI = 0.9
        CR = CI / RI if RI != 0 else 0

        if CR > 0.1:
            messages.error(request, 'CR lebih besar dari 0.1, silakan periksa kembali matriks perbandingan.')
            return redirect(request.path)

        # Pembuatan objek PerhitunganAHP setelah pengecekan CR
        perhitungan = PerhitunganAHP.objects.create(
            lambda_max=lambda_max,
            CI=CI,
            CR=CR
        )

        # Simpan matriks perbandingan dan bobot hanya setelah objek `perhitungan` dibuat
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                MatriksPerbandingan.objects.create(
                    perhitungan=perhitungan,
                    row_kriteria=f'C{i+1}',
                    column_kriteria=f'C{j+1}',
                    value=float(value)
                )

        for i, row in enumerate(normalized_matrix):
            for j, value in enumerate(row):
                MatriksNormalisasi.objects.create(
                    perhitungan=perhitungan,
                    row_kriteria=f'C{i+1}',
                    column_kriteria=f'C{j+1}',
                    normalized_value=value
                )

        for i, (weight, eigen_val) in enumerate(zip(weights, eigen_values)):
            column_sum = column_sums[i]

            BobotKriteria.objects.create(
                perhitungan=perhitungan,
                kriteria=f'C{i+1}',
                weight=weight,
                eigen_value=eigen_val,
                weighted_sum_matrix=weighted_sum_matrix[i]
            )
            
        messages.success(request, 'Berhasil menjalankan proses perhitungan!')
        return redirect('ahp:bobot_aktif')

    context = {
        'kriteria': kriteria,
    }

    return render(request, template_name, context)

def hitung_nilai_alternatif(ipk, penghasilan, tanggungan, usia):
    # Penilaian IPK (Benefit)
    if ipk >= 3.75:
        ipk_score = 4  # Sangat Baik
    elif 3.50 <= ipk <= 3.74:
        ipk_score = 3  # Baik
    elif 3.00 <= ipk <= 3.49:
        ipk_score = 2  # Cukup
    else:
        ipk_score = 1  # Kurang

    # Penilaian Penghasilan Orang Tua (Cost)
    if penghasilan < 1500000:
        penghasilan_score = 4  # Sangat Rendah
    elif 1500000 <= penghasilan <= 3000000:
        penghasilan_score = 3  # Rendah
    elif 3000001 <= penghasilan <= 4500000:
        penghasilan_score = 2  # Sedang
    else:
        penghasilan_score = 1  # Tinggi

    # Penilaian Jumlah Tanggungan (Benefit)
    if tanggungan >= 5:
        tanggungan_score = 4  # Sangat Banyak
    elif tanggungan == 4:
        tanggungan_score = 3  # Banyak
    elif tanggungan == 3:
        tanggungan_score = 2  # Cukup
    else:
        tanggungan_score = 1  # Sedikit

    # Penilaian Usia (Cost)
    if usia < 18:
        usia_score = 4  # Sangat Muda
    elif 18 <= usia <= 20:
        usia_score = 3  # Muda
    elif 21 <= usia <= 23:
        usia_score = 2  # Cukup Dewasa
    else:
        usia_score = 1  # Dewasa

    return ipk_score, penghasilan_score, tanggungan_score, usia_score

@login_required(login_url='/auth-login')
def proses_ranking(request):
    if not request.user.is_authenticated:
        return redirect('/')

    # Mengambil perhitungan terakhir yang sudah dibuat
    perhitungan = PerhitunganAHP.objects.latest('id')

    # Mengambil bobot untuk perhitungan ranking
    bobot = {}
    bobot_data_ipk = BobotKriteria.objects.filter(perhitungan=perhitungan, kriteria='C1').first()
    bobot['IPK'] = bobot_data_ipk.weight if bobot_data_ipk else 0

    bobot_data_penghasilan = BobotKriteria.objects.filter(perhitungan=perhitungan, kriteria='C2').first()
    bobot['Penghasilan'] = bobot_data_penghasilan.weight if bobot_data_penghasilan else 0

    bobot_data_tanggungan = BobotKriteria.objects.filter(perhitungan=perhitungan, kriteria='C3').first()
    bobot['Tanggungan'] = bobot_data_tanggungan.weight if bobot_data_tanggungan else 0

    bobot_data_usia = BobotKriteria.objects.filter(perhitungan=perhitungan, kriteria='C4').first()
    bobot['Usia'] = bobot_data_usia.weight if bobot_data_usia else 0

    # Mengambil mahasiswa yang memiliki data lengkap dan belum dihitung
    mahasiswa_list = Mahasiswa.objects.filter(
        ipk__isnull=False,
        penghasilan_orang_tua__isnull=False,
        jumlah_tanggungan__isnull=False,
        usia__isnull=False,
        is_calculated=False  # Hanya mahasiswa yang belum dihitung
    )

    mahasiswa_ranking = []

    # Reset status is_lolos ke None sebelum perhitungan
    for mahasiswa in mahasiswa_list:
        mahasiswa.is_lolos = None
        mahasiswa.save()

    for mahasiswa in mahasiswa_list:
        # Menghitung nilai total untuk mahasiswa
        ipk_score, penghasilan_score, tanggungan_score, usia_score = hitung_nilai_alternatif(
            mahasiswa.ipk, mahasiswa.penghasilan_orang_tua, mahasiswa.jumlah_tanggungan, mahasiswa.usia
        )
        nilai_total = (
            ipk_score * bobot['IPK'] +
            penghasilan_score * bobot['Penghasilan'] +
            tanggungan_score * bobot['Tanggungan'] +
            usia_score * bobot['Usia']
        )
        
        # Menyimpan total score dan rank di mahasiswa
        mahasiswa.total_score = nilai_total
        mahasiswa.save()  # Simpan total_score di database

        mahasiswa_ranking.append({
            'mahasiswa_id': mahasiswa.id,
            'nilai_total': nilai_total,
            'ranking': None
        })

        # Tandai mahasiswa sebagai sudah dihitung
        mahasiswa.is_calculated = True
        mahasiswa.save()  # Simpan status perhitungan selesai di database

    # Mengurutkan mahasiswa berdasarkan nilai total dan memberikan ranking
    mahasiswa_ranking.sort(key=lambda x: x['nilai_total'], reverse=True)
    for rank, item in enumerate(mahasiswa_ranking, 1):
        # Simpan rank untuk masing-masing mahasiswa
        mahasiswa = Mahasiswa.objects.get(id=item['mahasiswa_id'])
        mahasiswa.rank = rank
        mahasiswa.save()  # Simpan rank di database

        item['ranking'] = rank

    # Menangani input kuota melalui POST (tidak menggunakan JSON)
    if request.method == 'POST':
        kuota = int(request.POST.get('kuota'))

        if kuota and kuota > 0:
            # Update status mahasiswa berdasarkan kuota
            for mahasiswa in mahasiswa_ranking[:kuota]:
                mahasiswa_obj = Mahasiswa.objects.get(id=mahasiswa['mahasiswa_id'])
                mahasiswa_obj.is_lolos = True  # Lolos jika rankingnya masuk dalam kuota
                mahasiswa_obj.save()

            for mahasiswa in mahasiswa_ranking[kuota:]:
                mahasiswa_obj = Mahasiswa.objects.get(id=mahasiswa['mahasiswa_id'])
                mahasiswa_obj.is_lolos = False  # Ditolak jika rankingnya lebih dari kuota
                mahasiswa_obj.save()

            # Berikan pesan sukses setelah update
            messages.success(request, 'Kuota berhasil diterapkan!')
        else:
            messages.error(request, 'Kuota tidak valid!')

        # Redirect setelah berhasil
        return redirect('admin_mahasiswa_list')

    # Berikan pesan sukses untuk perhitungan ranking
    messages.success(request, 'Perhitungan dan ranking mahasiswa berhasil dihitung!')

    # Redirect ke daftar mahasiswa setelah proses selesai
    return redirect('admin_mahasiswa_list')

def bobot_aktif(request):
    if not request.user.is_authenticated:
        return redirect('/auth-login')

    # Ambil data perhitungan terbaru
    perhitungan = PerhitunganAHP.objects.all().last()  # Mengambil perhitungan terbaru
    
    if perhitungan is None:
        messages.error(request, 'Tidak ada perhitungan AHP yang tersedia.')

    # Ambil data matriks perbandingan, normalisasi, dan bobot untuk perhitungan yang dipilih
    matriks_perbandingan = MatriksPerbandingan.objects.filter(perhitungan=perhitungan)
    matriks_normalisasi = MatriksNormalisasi.objects.filter(perhitungan=perhitungan)
    bobot_kriteria = BobotKriteria.objects.filter(perhitungan=perhitungan)

    if not matriks_perbandingan or not matriks_normalisasi or not bobot_kriteria:
        messages.warning(request, 'Data matriks atau bobot belum tersedia.')

    kriteria = {
        'C1': '(C1) IPK',
        'C2': '(C2) Penghasilan',
        'C3': '(C3) Tanggungan',
        'C4': '(C4) Usia'
    }
    
    context = {
        'perhitungan': perhitungan,
        'matriks_perbandingan': matriks_perbandingan,
        'matriks_normalisasi': matriks_normalisasi,
        'bobot_kriteria': bobot_kriteria,
        'kriteria': kriteria
    }

    return render(request, 'dashboard/superadmin/bobot_aktif.html', context)

def bobot_history(request):
    if not request.user.is_authenticated:
        return redirect('/auth-login')
    template_name = "dashboard/superadmin/bobot_history.html"
    
    perhitungan = Bobot.objects.all()
    context = {
        "perhitungan": perhitungan
    }
    
    return render(request, template_name, context)

@login_required(login_url='/auth-login')
def biodata(request):
    template_name = "dashboard/pengguna/biodata.html"
    
    # Mengambil data mahasiswa yang sesuai dengan user yang sedang login
    mahasiswa = Mahasiswa.objects.filter(user=request.user).first()  # Menemukan mahasiswa berdasarkan user yang login
    # Periksa apakah ada mahasiswa yang perhitungannya sudah selesai
    perhitungan_selesai = Mahasiswa.objects.filter(is_calculated=True).exists()
    if mahasiswa:
        mahasiswa_data = {
            'first_name': mahasiswa.user.first_name,
            'last_name': mahasiswa.user.last_name,
            'ipk': mahasiswa.ipk,
            'penghasilan_orang_tua': mahasiswa.penghasilan_orang_tua,
            'jumlah_tanggungan': mahasiswa.jumlah_tanggungan,
            'usia': mahasiswa.usia,
            'is_lolos': mahasiswa.is_lolos,
            'rank': mahasiswa.rank
        }
    else:
        mahasiswa_data = None  # Jika data mahasiswa belum ada, kita set ke None

    # Menyiapkan form untuk mengedit data mahasiswa
    mahasiswa_form = MahasiswaForm(instance=mahasiswa)

    context = {
        'mahasiswa_data': mahasiswa_data,
        'mahasiswa_form': mahasiswa_form,
        "perhitungan_selesai": perhitungan_selesai
    }

    return render(request, template_name, context)

@login_required(login_url='/auth-login')
def edit_biodata(request):
    template = 'dashboard/pengguna/biodata.html'
    
    # Mengambil data mahasiswa yang sesuai dengan user yang sedang login
    mahasiswa = get_object_or_404(Mahasiswa, user=request.user)
    user = mahasiswa.user  # Mengambil user yang terkait dengan mahasiswa
    
    if request.method == 'POST':
        # Membuat form untuk mahasiswa
        mahasiswa_form = MahasiswaForm(request.POST, instance=mahasiswa)
        
        # Memeriksa apakah form mahasiswa valid
        if mahasiswa_form.is_valid():
            # Menyimpan data form mahasiswa
            mahasiswa_form.save()
            
            # Redirect ke halaman lain setelah sukses (misalnya ke halaman biodata)
            messages.success(request, 'Berhasil mengupdate data!')
            return redirect('ahp:biodata')
        
        else:
            # Jika form tidak valid, tampilkan pesan error dengan batasannya
            for field, errors in mahasiswa_form.errors.items():
                for error in errors:
                    # Menambahkan pesan error ke messages framework
                    messages.error(request, f"Kesalahan pada {field.capitalize()}: {error}")
                    
    else:
        # Membuat form dengan data yang ada
        mahasiswa_form = MahasiswaForm(instance=mahasiswa)
    
    context = {
        'mahasiswa_form': mahasiswa_form,
        'mahasiswa': mahasiswa,  # Kirimkan objek mahasiswa untuk ditampilkan di template
        'user': user
    }

    return render(request, template, context)

def buka_beasiswa(request):
    if not request.user.is_authenticated:
        return redirect('/')  # Pastikan hanya admin yang bisa melakukannya
    try:
        # Mengubah status is_calculated dari 1 menjadi 0 untuk semua mahasiswa
        mahasiswa_list = Mahasiswa.objects.filter(is_calculated=1)  # Ambil mahasiswa yang sudah dihitung
        if mahasiswa_list.exists():
            mahasiswa_list.update(is_calculated=0, rank=None, total_score=None,is_lolos=None)  # Set status is_calculated menjadi False
            messages.success(request, "Pendaftaran telah dibuka kembali.")
        else:
            messages.warning(request, "Tidak ada perhitungan yang perlu direset.")
    except Exception as e:
        messages.error(request, f"Terjadi kesalahan: {str(e)}")

    return redirect('admin_mahasiswa_list')  # Redirect ke halaman yang sesuai (misalnya dashboard)