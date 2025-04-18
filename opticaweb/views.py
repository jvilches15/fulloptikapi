from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import UserProfile
from django.http import JsonResponse
from .forms import EditProfileForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import Comuna

Usuario = get_user_model()

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso.')
            return redirect('index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'login.html')

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def adulto(request):
    return render(request, 'category-adulto.html')

@login_required
def infantil(request):
    return render(request, 'category-infantil.html')

@login_required
def sobrelentes(request):
    return render(request, 'category-sobrelentes.html')

@login_required
def sol(request):
    return render(request, 'category-lentessol.html')

@login_required
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
    
@login_required(login_url='login')
def editar_perfil(request):
    perfil = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        if 'delete_account' in request.POST:
            user = request.user
            logout(request)
            user.delete()
            messages.warning(request, "Tu cuenta ha sido eliminada correctamente.")
            return redirect('index')

        form = EditProfileForm(request.POST, request.FILES, instance=perfil, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('perfil')
    else:
        form = EditProfileForm(instance=perfil, user=request.user)

    return render(request, 'editar_perfil.html', {'form': form})

def cargar_comunas(request):
    region_id = request.GET.get('region_id')
    comunas = Comuna.objects.filter(region_id=region_id).values('id', 'nombre')
    return JsonResponse(list(comunas), safe=False)

def reset_password_page(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        nueva_contraseña = request.POST.get('nueva_contraseña')

        try:
            usuario = Usuario.objects.get(username=rut)
            usuario.password = make_password(nueva_contraseña)
            usuario.save()
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('index')
        except Usuario.DoesNotExist:
            messages.error(request, 'No se encontró un usuario con ese RUT.')

    return render(request, 'reset_password.html')

def cerrar_sesion(request):
    logout(request)
    return redirect('index')



# Create your views here.
