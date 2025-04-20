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
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import Http404
from .models import Producto
from .models import Venta
from .forms import CitaForm
from .models import Cita
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages


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
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        rut = request.POST.get('rut')
        fecha_nacimiento = request.POST.get('date_of_birth')
        direccion = request.POST.get('address')
        region_id = request.POST.get('region')
        comuna_id = request.POST.get('comuna')
        imagen = request.FILES.get('image')
     

       
        user = User.objects.create_user(
            username=rut,
            first_name=nombre,
            password='temporal123'  
        )

       
        UserProfile.objects.create(
            user=user,
            rut=rut,
            date_of_birth=fecha_nacimiento,
            address=direccion,
            region_id=region_id,
            comuna_id=comuna_id,
            image=imagen,
            
        )

        messages.success(request, "Usuario creado correctamente.")
        return redirect('panel_administrador')

 
    regiones = Region.objects.all()
    comunas = Comuna.objects.all()
    return render(request, 'crear_usuario.html', {
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



# Create your views here.
