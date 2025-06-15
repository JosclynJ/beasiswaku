from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from ahp.models import *
from user.models import *
from django.contrib import  messages
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.

def home(request):
    template_name = "login/index.html"
    context = {
    }
    
    return render(request, template_name, context)

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/auth-login')
    template_name = "dashboard/index.html"
    mahasiswa = Mahasiswa.objects.filter(user=request.user).first()  # Menemukan mahasiswa berdasarkan user yang login
    perhitungan_selesai = Mahasiswa.objects.filter(is_calculated=True).exists()
    # Ambil data untuk statistik
    total_mahasiswa = Mahasiswa.objects.count()
    total_pendaftar = Mahasiswa.objects.filter(
    ipk__isnull=False,
    penghasilan_orang_tua__isnull=False,
    jumlah_tanggungan__isnull=False,
    usia__isnull=False
    ).count()
    
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
    
    total_lolos = Mahasiswa.objects.filter(is_lolos='1').count()
    total_ditolak = Mahasiswa.objects.filter(is_lolos='0').count()
    perhitungan_selesai = Mahasiswa.objects.filter(is_calculated=True).exists()
    persenan_daftar = (total_pendaftar / total_mahasiswa) * 100 if total_pendaftar else 0
    if total_lolos == 0:
        persenan_lolos = "Data belum ada"
    else:
        persenan_lolos = (total_pendaftar / total_lolos) * 100

    context = {
        'total_mahasiswa': total_mahasiswa,
        'total_pendaftar': total_pendaftar,
        'total_lolos': total_lolos,
        'total_ditolak': total_ditolak,
        'perhitungan_selesai': perhitungan_selesai,
        'persenan_daftar': persenan_daftar,
        'persenan_lolos': persenan_lolos,
        'mahasiswa_data': mahasiswa_data,
    }
    return render(request, template_name, context)

@login_required
def ubah_password(request):
    template_name = "dashboard/ubah_password.html"
    
    if request.method == 'POST':
        form = UbahPasswordForm(request.POST)
        
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            
            # Validasi password lama
            if not request.user.check_password(current_password):
                messages.error(request, 'Password sekarang yang Anda masukkan salah!')
                return redirect('ubah_password')  # Redirect agar user bisa mengoreksi

            # Validasi password baru dan konfirmasi password
            if new_password != confirm_password:
                messages.error(request, 'Password baru dan konfirmasi password tidak cocok!')
                return redirect('ubah_password')  # Redirect agar user bisa mengoreksi

            # Jika validasi berhasil, update password
            request.user.set_password(new_password)
            request.user.save()

            messages.success(request, 'Password berhasil diubah! Silahkan login kembali.')
            return redirect('login')  # Arahkan user untuk login kembali setelah perubahan password
        else:
            # Jika form tidak valid, pesan error akan ditangani di dalam form
            pass
    else:
        form = UbahPasswordForm()
    
    context = {
        'form': form
    }

    return render(request, template_name, context)

def handle_404(request, path):
    return render(request, '404.html', {'path': path}, status=404)