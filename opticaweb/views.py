from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from django.contrib.auth import authenticate, login

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
            # Guardar el nuevo usuario en la base de datos
            form.save()
            # Redirigir al usuario a la página de perfil o login después de registrar
            return redirect('perfil')  # Redirige al perfil
     else:
        form = UserProfileForm()
    
     return render(request, 'registro.html', {'form': form})

@login_required
def perfil(request):
    if request.method == 'POST':
        rut = request.POST['rut']
        password = request.POST['password']

        user = authenticate(request, username=rut, password=password)

        if user is not None:
            login(request, user)
            return redirect('perfil')  
        else:
            return render(request, 'login.html', {'error': 'RUT o contraseña incorrectos'})
    
    return render(request, 'login.html')

def reset_password(request):
    return render(request, 'reset_password.html')
# Create your views here.
