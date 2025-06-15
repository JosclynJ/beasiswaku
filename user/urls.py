from django.urls import path
from user.views import *
urlpatterns = [
    ############################## fungsi superadmin ##############################
    path('superadmin/admin/list', superadmin_admin_list, name='superadmin_admin_list'),
    path('superadmin/admin/tambah', superadmin_admin_tambah, name='superadmin_admin_tambah'),
    path('superadmin/admin/edit/<int:user_id>/', superadmin_admin_edit, name='superadmin_admin_edit'),
    path('superadmin/admin/hapus/<int:user_id>/', superadmin_admin_hapus, name='superadmin_admin_hapus'),
    
    ############################## fungsi admin ##############################
    path('admin/mahasiswa/list', admin_mahasiswa_list, name='admin_mahasiswa_list'),
    path('admin/mahasiswa/list-edit/<int:user_id>/', admin_mahasiswa_list_edit, name='admin_mahasiswa_list_edit'),
    path('admin/mahasiswa/akun-list', admin_mahasiswa_akun_list, name='admin_mahasiswa_akun_list'),
    path('admin/mahasiswa/akun-tambah', admin_mahasiswa_akun_tambah, name='admin_mahasiswa_akun_tambah'),
    path('admin/mahasiswa/akun-edit/<int:user_id>/', admin_mahasiswa_akun_edit, name='admin_mahasiswa_akun_edit'),
    path('admin/mahasiswa/akun-hapus/<int:user_id>/', admin_mahasiswa_akun_hapus, name='admin_mahasiswa_akun_hapus'),
]