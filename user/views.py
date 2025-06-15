from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import  messages
from .models import *
from .forms import *
from ahp.forms import *

def in_admin(user):
    get_user = user.groups.filter(name='admin').count()
    if get_user > 0:
        return True
    else:
        return False
    
def in_superadmin(user):
    get_user = user.groups.filter(name='superadmin').count()
    if get_user > 0:
        return True
    else:
        return False

def in_admin_or_superadmin(user):
    return in_admin(user) or in_superadmin(user)


@login_required(login_url='/auth-login')
@user_passes_test(in_superadmin, login_url='/')
def superadmin_admin_list(request):
    template_name = "dashboard/superadmin/admin_list.html"
    
    admin_group = Group.objects.get(name='admin')
    
    # Ambil semua user yang tergabung dalam group "admin"
    daftar_admin = User.objects.filter(groups=admin_group).exclude(is_superuser=True)

    context = {
        "daftar_admin": daftar_admin
    }

    return render(request, template_name, context)

@login_required(login_url='/auth-login')
@user_passes_test(in_superadmin, login_url='/')
def superadmin_admin_tambah(request):
    template_name = "dashboard/superadmin/admin_akun_forms.html"

    if request.method == "POST":
        form = AdminForm(request.POST)

        # Cek apakah form sudah di-bind dan ambil username dari form
        if form.is_bound:
            username = form.data.get('username')  # Ambil username dari data form yang di-submit

            # Cek apakah username sudah ada di database
            if username and User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' sudah digunakan. Silakan pilih username lain.")
                return redirect('superadmin_admin_tambah')  # Redirect ke halaman form lagi untuk perbaikan

        # Jika username tidak duplikat, lanjutkan validasi form
        if form.is_valid():
            username = form.cleaned_data['username']  # Ambil username dari form yang sudah divalidasi
            password = username  # Set password yang sama dengan username
            
            # Buat user baru jika form valid
            user = User.objects.create_user(username=username)  # Buat user dengan username
            user.set_password(password)  # Set password yang sama dengan username
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            # Menambahkan user ke group "Admin" setelah akun dibuat
            group = Group.objects.get(name='Admin')
            user.groups.add(group)

            messages.success(request, 'Akun admin berhasil dibuat!')
            return redirect('superadmin_admin_list')  # Arahkan ke halaman daftar akun admin setelah berhasil
        else:
            messages.error(request, 'Formulir tidak valid. Harap periksa inputan Anda.')  # Pesan error jika form tidak valid
    
    else:
        form = AdminForm()

    context = {
        "form": form,
    }

    return render(request, template_name, context)

@login_required(login_url='/auth-login')
@user_passes_test(in_superadmin, login_url='/')
def superadmin_admin_edit(request, user_id):
    template_name = "dashboard/superadmin/admin_akun_forms.html"
    # Ambil user berdasarkan user_id
    user = get_object_or_404(User, id=user_id)

    # Cek jika user yang sedang login adalah user yang sedang diedit
    if user == request.user:
        pass
    
    if request.method == "POST":
        form = AdminForm(request.POST, instance=user)
        if form.is_valid():
            # Update hanya first_name dan last_name, menjaga agar username tidak diubah
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            
            # Cek password, hanya update jika ada input
            if form.cleaned_data['password1']:
                user.set_password(form.cleaned_data['password1'])
            
            # Simpan perubahan data user
            user.save()

            # Simpan perubahan data mahasiswa terkait dengan user yang baru diperbarui
            form.save()  # Mahasiswa sudah terhubung dengan user yang baru diperbarui

            messages.success(request, 'Akun berhasil diperbarui!')
            return redirect('superadmin_admin_list')  # Redirect ke daftar akun setelah berhasil
        else:
            messages.error(request, 'Formulir tidak valid. Harap periksa inputan Anda.')
    else:
        form = AdminForm(instance=user)  # Mengirimkan instance user ke form untuk edit

    context = {
        "form": form,
    }

    return render(request, template_name, context)

@login_required(login_url='/auth-login')
@user_passes_test(in_superadmin, login_url='/')
def superadmin_admin_hapus(request, user_id):
    try:
        # Ambil objek User berdasarkan user_id
        user = get_object_or_404(User, id=user_id)

        # Hapus data user
        username = user.username  # Menyimpan username untuk pesan sukses

        # Menghapus user
        user.delete()

        messages.success(request, f'Akun pengguna {username} berhasil dihapus!')
    except User.DoesNotExist:
        messages.error(request, 'Akun pengguna tidak ditemukan.')
    except Exception as e:
        messages.error(request, 'Terjadi kesalahan saat menghapus akun pengguna.')

    return redirect('superadmin_admin_list')  # Redirect ke daftar akun pengguna setelah berhasil

@login_required(login_url='/auth-login')
@user_passes_test(in_admin_or_superadmin, login_url='/')
def admin_mahasiswa_list(request):
    template_name = "dashboard/admin/mahasiswa_list.html"
    
    # Periksa apakah ada mahasiswa yang perhitungannya sudah selesai
    perhitungan_selesai = Mahasiswa.objects.filter(is_calculated=True).exists()
    
    # Ambil ranking mahasiswa dari session jika ada
    mahasiswa_ranking = request.session.get('mahasiswa_ranking', [])
    
    # Ambil daftar mahasiswa dari database
    daftar_mahasiswa = Mahasiswa.objects.filter(
        ipk__isnull=False,
        penghasilan_orang_tua__isnull=False,
        jumlah_tanggungan__isnull=False,
        usia__isnull=False
    )


    context = {
        "daftar_mahasiswa": daftar_mahasiswa,
        "mahasiswa_ranking": mahasiswa_ranking,  # Kirimkan ranking ke template
        "perhitungan_selesai": perhitungan_selesai,
    }

    return render(request, template_name, context)

@login_required(login_url='/auth-login')
@user_passes_test(in_admin_or_superadmin, login_url='/')
def admin_mahasiswa_tambah(request):
    template_name = "dashboard/admin/mahasiswa_tambah.html"
    daftar_mahasiswa = Mahasiswa.objects.all()
    
    context = {
        "daftar_mahasiswa": daftar_mahasiswa
    }
    return render(request, template_name, context)

@login_required(login_url='/auth-login')
@user_passes_test(in_admin_or_superadmin, login_url='/')
def admin_mahasiswa_list_edit(request, user_id):
    template_name = "dashboard/admin/mahasiswa_list_edit.html"
    mahasiswa = get_object_or_404(Mahasiswa, user_id=user_id)
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
            return redirect('admin_mahasiswa_list')
        
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
        'forms': mahasiswa_form,
        'mahasiswa': mahasiswa,
    }

    return render(request, template_name, context)

@login_required(login_url='/auth-login')
@user_passes_test(in_admin_or_superadmin, login_url='/')
def admin_mahasiswa_akun_list(request):
    template_name = "dashboard/admin/mahasiswa_akun_list.html"
    daftar_mahasiswa = Mahasiswa.objects.select_related('user').all()
    context = {
        "daftar_mahasiswa": daftar_mahasiswa
    }
    return render(request, template_name, context)

@login_required(login_url='/auth-login')
@user_passes_test(in_admin_or_superadmin, login_url='/')
def admin_mahasiswa_akun_tambah(request):
    template_name = "dashboard/admin/mahasiswa_akun_forms.html"
    
    if request.method == "POST":
        form = MahasiswaUserForm(request.POST)

        if form.is_valid():
            nim = form.cleaned_data['nim']  # Ambil NIM dari form yang sudah diinputkan
            password = nim  # Set password yang sama dengan NIM

            # Debugging: Tampilkan password yang dimasukkan
            print(f"Password yang dimasukkan (sebelum enkripsi): {password}")  # Debugging: Menampilkan password sebelum diset

            # Cek apakah NIM sudah terdaftar di database
            if User.objects.filter(username=nim).exists():
                # Jika NIM sudah terdaftar, tampilkan pesan error
                messages.error(request, f"Username (NIM) '{nim}' sudah digunakan. Silakan pilih NIM lain.")
                return redirect('admin_mahasiswa_akun_tambah')  # Redirect ke halaman form lagi untuk perbaikan

            # Jika form valid dan NIM tidak duplikat, simpan data
            user = User.objects.create_user(username=nim)  # Buat user dengan NIM sebagai username
            
            # Debugging: Menampilkan password sebelum enkripsi
            print(f"Password sebelum enkripsi: {password}")

            # Set password yang sama dengan NIM
            user.set_password(password)  # Set password yang sama dengan NIM
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            # Debugging: Tampilkan password terenkripsi
            print(f"Password terenkripsi yang disimpan: {user.password}")  # Debugging: Menampilkan password terenkripsi

            # Menambahkan user ke group tertentu setelah akun dibuat
            group = Group.objects.get(name='User')  # Ganti dengan nama group sesuai kebutuhan
            user.groups.add(group)

            # Simpan data mahasiswa dan hubungkan dengan user yang baru dibuat
            mahasiswa = Mahasiswa(user=user)
            mahasiswa.save()

            messages.success(request, 'Akun mahasiswa berhasil dibuat!')
            return redirect('admin_mahasiswa_akun_list')  # Arahkan ke halaman daftar akun mahasiswa setelah berhasil
        else:
            print("Form is not valid. Errors:", form.errors)  # Menampilkan error form jika ada
            messages.error(request, 'Formulir tidak valid. Harap periksa inputan Anda.')  # Pesan error
    else:
        form = MahasiswaUserForm()

    context = {
        "form": form
    }
    return render(request, template_name, context)

@login_required(login_url='/auth-login')
@user_passes_test(in_admin_or_superadmin, login_url='/')
def admin_mahasiswa_akun_edit(request, user_id):
    template_name = "dashboard/admin/mahasiswa_akun_forms.html"
    
    # Ambil objek Mahasiswa berdasarkan user_id (ForeignKey ke User)
    mahasiswa = get_object_or_404(Mahasiswa, user_id=user_id)
    user = mahasiswa.user  # Mengambil user yang terkait dengan mahasiswa
    
    if request.method == "POST":
        form = MahasiswaUserForm(request.POST, instance=user)

        if form.is_valid():
            # Simpan perubahan, termasuk username (nim)
            nim = form.cleaned_data['nim']
            user.username = nim  # Pastikan nim diassign ke username
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.set_password(form.cleaned_data['password1'])  # Jika password diubah, kita gunakan set_password
            user.save()

            # Simpan perubahan data mahasiswa
            form.save()  # Mahasiswa sudah terhubung dengan user yang baru diperbarui

            messages.success(request, 'Akun mahasiswa berhasil diperbarui!')
            return redirect('admin_mahasiswa_akun_list')  # Redirect ke daftar akun mahasiswa setelah berhasil
        else:
            messages.error(request, 'Formulir tidak valid. Harap periksa inputan Anda.')
    else:
        form = MahasiswaUserForm(instance=user)  # Mengirimkan instance user ke form untuk edit

    context = {
        "form": form,
        "mahasiswa": mahasiswa  # Menyertakan data mahasiswa yang diedit
    }

    return render(request, template_name, context)

@login_required(login_url='/auth-login')
@user_passes_test(in_admin_or_superadmin, login_url='/')
def admin_mahasiswa_akun_hapus(request, user_id):
    try:
        # Ambil objek Mahasiswa dan User berdasarkan user_id
        mahasiswa = get_object_or_404(Mahasiswa, user_id=user_id)
        user = mahasiswa.user  # Mengambil user yang terkait dengan mahasiswa

        # Hapus data mahasiswa
        mahasiswa.delete()

        # Hapus data user
        user.delete()

        messages.success(request, f'Akun mahasiswa {user.username} berhasil dihapus!')
    except Mahasiswa.DoesNotExist:
        messages.error(request, 'Akun mahasiswa tidak ditemukan.')
    except Exception as e:
        messages.error(request, 'Akun mahasiswa tidak ditemukan.')

    return redirect('admin_mahasiswa_akun_list')  # Redirect ke daftar akun mahasiswa setelah berhasil
