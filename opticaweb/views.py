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
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Consejo
from .models import Promocion
from .serializers import ConsejoSerializer
from .serializers import PromocionSerializer
import requests
from django.views.decorators.csrf import csrf_exempt
import requests
from .permissions import SoloLecturaOAutenticado
from .decorators import solo_admin, solo_colaborador
from openpyxl import Workbook
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import pandas as pd
from .models import User
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import os
from django.conf import settings


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


@solo_admin
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

def lista_usuarioss(request):
  
    usuarios = User.objects.filter(is_staff=False)  
    return render(request, 'lista_usuarioss.html', {'usuarios': usuarios})


@solo_admin
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

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.contrib.auth.models import User
import os
from django.conf import settings

def reporte_usuarios_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_usuarios.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

   
    logo_path = os.path.join(settings.BASE_DIR, 'opticaweb', 'static', 'img', 'Full-optik.jpg')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=1.5*inch, height=1.0*inch)
        img.hAlign = 'CENTER'
        elements.append(img)

   
    title = Paragraph("Reporte de Usuarios", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    
    data = [[
        "RUT", "Nombre", "Email", "Nacimiento", "Dirección", "Región", "Comuna"
    ]]

    
    usuarios = User.objects.filter(is_staff=False)
    for u in usuarios:
        perfil = getattr(u, 'userprofile', None)
        if perfil:
            data.append([
                perfil.rut,
                u.get_full_name(),
                u.email,
                perfil.date_of_birth.strftime('%d-%m-%Y') if perfil.date_of_birth else '',
                perfil.address,
                perfil.region.nombre if perfil.region else '',
                perfil.comuna.nombre if perfil.comuna else '',
            ])

    
    table = Table(data, repeatRows=1, colWidths=[70, 100, 120, 70, 100, 70, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498db")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))

    elements.append(table)
    doc.build(elements)

    return response


def reporte_usuarios_excel(request):
    usuarios = User.objects.filter(is_staff=False)

    data = []
    for u in usuarios:
        perfil = getattr(u, 'userprofile', None)
        if perfil:
            data.append({
                'RUT': perfil.rut,
                'Nombre': u.get_full_name(),
                'Email': u.email,
                'Nacimiento': perfil.date_of_birth.strftime('%d-%m-%Y') if perfil.date_of_birth else '',
                'Dirección': perfil.address,
                'Comuna': perfil.comuna.nombre if perfil.comuna else '',
                'Región': perfil.region.nombre if perfil.region else '',
            })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="usuarios.xlsx"'
    df.to_excel(response, index=False)

    return response


@solo_colaborador
def reporte_productos_excel(request):
    productos = Producto.objects.all()
    wb = Workbook()
    ws = wb.active
    ws.title = "Productos"

    ws.append(['Nombre', 'Descripcion', 'Precio', 'Stock'])

    for p in productos:
        ws.append([p.nombre, p.descripcion, p.precio, p.stock])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="productos.xlsx"'
    wb.save(response)
    return response

@solo_colaborador
def reporte_productos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_productos.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    
    logo_path = os.path.join(settings.BASE_DIR, 'opticaweb', 'static', 'img', 'Full-optik.jpg')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=1.5*inch, height=1.0*inch)
        img.hAlign = 'CENTER'
        elements.append(img)

   
    title = Paragraph("Reporte de Productos", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

   
    data = [["Nombre", "Descripción", "Precio", "Stock"]]

   
    productos = Producto.objects.all()
    for p in productos:
        data.append([
            p.nombre,
            p.descripcion,
            f"${p.precio:,.0f}",
            p.stock
        ])

    
    table = Table(data, repeatRows=1, colWidths=[120, 200, 70, 50])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2ecc71")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements)
    return response


def panel_administrador(request):
    if request.session.get('admin_user_id'):
        productos = Producto.objects.all()  
        return render(request, 'panel_administrador.html', {'productos': productos})  
    return redirect('admin_login')


def panel_colaborador(request):
    if request.session.get('admin_user_id'):
        citas = Cita.objects.all()
        return render(request, 'panel_colaborador.html', {'citas': citas})
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

@solo_admin
def eliminar_producto(request, producto_id):
    if request.session.get('admin_user_rol') != 'administrador':
        return redirect('panel_usuario')

    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    return redirect('panel_administrador')


@solo_admin
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'lista_productos.html', {'productos': productos})

@solo_colaborador
def lista_productoss(request):
    productos = Producto.objects.all()
    return render(request, 'lista_productoss.html', {'productos': productos})

def lista_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'lista_ventas.html', {'ventas': ventas})

@solo_admin
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    usuario.delete()
    messages.success(request, 'Usuario eliminado correctamente.')
    return redirect('lista_usuarios')

@solo_admin
def eliminar_producto(request, producto_id):
    if request.method == 'POST' and request.session.get('admin_user_rol') == 'administrador':
        producto = get_object_or_404(Producto, id=producto_id)
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente.')
    return redirect('lista_productos')

@solo_colaborador 
def gestionar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in ['pendiente', 'confirmada', 'rechazada']:
            cita.estado = nuevo_estado
            cita.save()
            messages.success(request, f"Estado de la cita actualizado a {nuevo_estado}.")
            
            
            return redirect('panel_colaborador')  

    return render(request, 'gestionar_cita.html', {'cita': cita})

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

def clima_view(request):
    return render(request, 'clima.html')

def ver_promociones(request):
    promociones = Promocion.objects.all()
    return render(request, 'promociones.html', {'promociones': promociones})

class PromocionListCreateAPIView(ListCreateAPIView):
    queryset = Promocion.objects.all()
    serializer_class = PromocionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  

class PromocionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Promocion.objects.all()
    serializer_class = PromocionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  


# Create your views here.
