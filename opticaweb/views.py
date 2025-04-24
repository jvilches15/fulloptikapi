from django.shortcuts import render, get_object_or_404, redirect
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
from .models import AdministracionUser
from .models import Region, Comuna
from django.db.models import Q
from django.http import Http404
from .models import Producto
from .models import Venta
from .forms import CitaForm
from .models import Cita
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import re
from django.core.exceptions import ValidationError
from .forms import RestablecerContrasenaForm
from .forms import CrearUsuarioForm
from rest_framework import viewsets
from .models import Consejo
from .serializers import ConsejoSerializer
import requests
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import requests
from rest_framework.response import Response
from .permissions import SoloLecturaOAutenticado



def es_admin(user):
    return user.is_superuser
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




def admin_login(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        password = request.POST.get('password')

        try:
            user = AdministracionUser.objects.get(rut=rut)
            if user.password == password:
               
                request.session['admin_user_id'] = user.id
                request.session['admin_user_rol'] = user.rol  

                if user.rol == 'administrador':
                    return redirect('panel_administrador')
                elif user.rol == 'colaborador':
                    return redirect('panel_colaborador')
                else:
                    messages.error(request, 'Rol desconocido.')
            else:
                messages.error(request, 'Contraseña incorrecta.')
        except AdministracionUser.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')

    return render(request, 'login_admin.html')



def crear_usuario(request):
    regiones = Region.objects.all()
    comunas = Comuna.objects.all()

    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST, request.FILES, regiones=regiones, comunas=comunas)
        if form.is_valid():
            cd = form.cleaned_data

            user = User.objects.create_user(
                username=cd['rut'],
                first_name=cd['nombre'],
                email=cd['email'],
                password=cd['password']
            )

            UserProfile.objects.create(
                user=user,
                rut=cd['rut'],
                date_of_birth=cd['date_of_birth'],
                address=cd['address'],
                region_id=cd['region'],
                comuna_id=cd['comuna'],
                image=cd['image']
            )

            messages.success(request, "Usuario creado correctamente.")
            return redirect('panel_administrador')
    else:
        form = CrearUsuarioForm(regiones=regiones, comunas=comunas)

    return render(request, 'crear_usuario.html', {
        'form': form,
        'regions': regiones,
        'comunas': comunas
    })
 

def lista_usuarios(request):
  
    usuarios = User.objects.filter(is_staff=False)  
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})

def lista_usuarios_colab(request):
  
    usuarios = User.objects.filter(is_staff=False)  
    return render(request, 'lista_usuarios_colab.html', {'usuarios': usuarios})



def ingresar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        imagen = request.FILES.get('imagen')

       
        producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            imagen=imagen
        )
        producto.save()

        messages.success(request, 'Producto agregado correctamente')
        return redirect('panel_administrador')

    return render(request, 'ingresar_producto.html')



def panel_administrador(request):
    if request.session.get('admin_user_id'):
        productos = Producto.objects.all()  
        return render(request, 'panel_administrador.html', {'productos': productos})  
    return redirect('admin_login')


def panel_colaborador(request):
    if request.session.get('admin_user_id'):
        return render(request, 'panel_colaborador.html')
    return redirect('admin_login')

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
            return redirect('login')
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

   
    citas = perfil.citas.all().order_by('-fecha')

    return render(request, 'perfil.html', {
        'user': request.user,
        'userprofile': perfil,
        'form': form,
        'citas': citas
    })
    
@login_required(login_url='login')
def editar_perfil(request):
    perfil = UserProfile.objects.get(user=request.user)

   
    if request.method == 'POST' and 'delete_account' in request.POST:
        user = request.user
        logout(request)
        user.delete()
        messages.warning(request, "Tu cuenta ha sido eliminada correctamente.")
        return redirect('index')

   
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=perfil, user=request.user)

     
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Perfil actualizado correctamente.")

           
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')

            if password and password == password_confirm:
                user = request.user
                user.set_password(password)  
                user.save()
                update_session_auth_hash(request, user) 
                messages.success(request, "Contraseña actualizada correctamente.")

            return redirect('perfil')

        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')

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

def eliminar_producto(request, producto_id):
    
    producto = get_object_or_404(Producto, id=producto_id)

    
    if request.method == 'POST':
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect('lista_productos')  

  
    return render(request, 'confirmar_eliminacion_producto.html', {'producto': producto})

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'lista_productos.html', {'productos': productos})

def lista_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'lista_ventas.html', {'ventas': ventas})

@login_required
def agendar_cita(request):
    user_profile = request.user.userprofile

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.usuario = user_profile
            cita.save()
            messages.success(request, "¡Cita agendada exitosamente!")
            return redirect('index')  
    else:
        form = CitaForm()

    return render(request, 'agendar_cita.html', {'form': form})

@login_required
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user.userprofile)

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, "Cita modificada correctamente.")
            return redirect('perfil')
    else:
        form = CitaForm(instance=cita)

    return render(request, 'editar_cita.html', {'form': form})

@login_required
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user.userprofile)

    if request.method == 'POST':
        cita.delete()
        messages.success(request, "Cita eliminada.")
        return redirect('perfil')

    return render(request, 'eliminar_cita.html', {'cita': cita})

def cerrar_sesion(request):
    logout(request)
    return redirect('index')


#API
class ConsejoViewSet(viewsets.ModelViewSet):
    queryset = Consejo.objects.all()
    serializer_class = ConsejoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    permission_classes = [SoloLecturaOAutenticado]
    

    
def consejos_view(request):
    url = "http://127.0.0.1:8000/api/consejos/"
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            consejos = response.json()  
        else:
            consejos = []  
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los consejos: {e}")
        consejos = []  
    
   
    return render(request, 'consejos.html', {'consejos': consejos})

@csrf_exempt
@api_view(['GET', 'POST'])
def consejos_list(request):
    if request.method == 'GET':
        consejos = Consejo.objects.all()
        serializer = ConsejoSerializer(consejos, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
      
        if not request.user.is_authenticated:
            return JsonResponse({'detail': 'No autorizado'}, status=401)
        
        serializer = ConsejoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)




@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def consejo_detail(request, id):
    try:
        consejo = Consejo.objects.get(id=id)
    except Consejo.DoesNotExist:
        return JsonResponse({'message': 'Consejo no encontrado'}, status=404)

    if request.method == 'GET':
        serializer = ConsejoSerializer(consejo)
        return JsonResponse(serializer.data)

    
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'No autorizado'}, status=401)

    if request.method == 'PUT':
        serializer = ConsejoSerializer(consejo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        consejo.delete()
        return JsonResponse({'message': 'Consejo eliminado'}, status=204)




def recetas_saludables_view(request):
   
    busqueda = request.GET.get('q', '')  
    
    
    if busqueda:
        url = f'https://www.themealdb.com/api/json/v1/1/search.php?s={busqueda}'
    else:
        url = 'https://www.themealdb.com/api/json/v1/1/filter.php?i=carrot'  
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            recetas = data.get('meals', [])  
        else:
            recetas = []
    except Exception as e:
        print(f"Error al obtener recetas: {e}")
        recetas = []

    return render(request, 'recetas.html', {'recetas': recetas, 'busqueda': busqueda})



# Create your views here.
