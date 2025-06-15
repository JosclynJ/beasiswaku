from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

def login(request):
    template_name = "login/index.html"
    pesan = ""
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            pesan = "Username dan Password Wajib Diisi!"
        else:
            user = authenticate(username=username, password=password)
            if user:
                auth_login(request, user)
                pesan = "Berhasil Login"
                return redirect('/dashboard')
            else:
                pesan = "Username atau Password Salah!"
        
    context = {
        "pesan": pesan
    }
    return render(request, template_name, context)

def logout(request):
    auth_logout(request)
    return redirect('/')