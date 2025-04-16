from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import UserProfile
from django.http import JsonResponse

def index(request):
    return render(request, 'index.html')

def adulto(request):
    return render(request, 'category-adulto.html')

def infantil(request):
    return render(request, 'category-infantil.html')

def sobrelentes(request):
    return render(request, 'category-sobrelentes.html')

def sol(request):
    return render(request, 'category-lentessol.html')

def nosotros(request):
    return render(request, 'nosotros.html')

def registro(request):
     if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('perfil')
     else:
        form = UserProfileForm()
    
     return render(request, 'registro.html', {'form': form})

@login_required(login_url='login')
def perfil(request):
    perfil, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST' and request.FILES:
        form = UserProfileForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil')  
    else:
        form = UserProfileForm(instance=perfil)

    return render(request, 'perfil.html', {
        'user': request.user,
        'userprofile': perfil,
        'form': form
    })
def cerrar_sesion(request):
    logout(request)
    return redirect('index')



# Create your views here.
