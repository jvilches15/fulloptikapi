from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Region, Comuna, Cita
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re



def validar_rut_chileno(value):
    if not re.match(r"^\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]$", value):
        raise ValidationError("Ingrese un RUT válido. Ej: 12.345.678-9")

def validar_password_segura(password):
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Debe contener al menos una letra mayúscula.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Debe contener al menos una letra minúscula.")
    if not re.search(r"\d", password):
        raise ValidationError("Debe contener al menos un número.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError("Debe contener al menos un símbolo.")

class RestablecerContrasenaForm(forms.Form):
    rut = forms.CharField(max_length=20, label='RUT')
    nueva_contraseña = forms.CharField(widget=forms.PasswordInput, label='Nueva contraseña', help_text="Debe ser de 8 caracteres, con mayúsculas, minúsculas, números y simbolos.")

    def clean_nueva_contraseña(self):
        contraseña = self.cleaned_data.get('nueva_contraseña')
        validar_password_segura(contraseña)  

class UserProfileForm(forms.ModelForm):
    full_name = forms.CharField(label="Nombre Completo")
    rut = forms.CharField(label="RUT", help_text="Formato: 12.345.678-9", validators=[validar_rut_chileno])
    email = forms.EmailField(label="Correo Electrónico", help_text="Formato: user@dominio.cl", validators=[validate_email])
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", help_text="Debe ser de 8 caracteres, con mayúsculas, minúsculas, números y simbolos.", validators=[validar_password_segura])
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha de nacimiento")
    address = forms.CharField(label="Dirección")
    region = forms.ModelChoiceField(queryset=Region.objects.all(), label="Región", required=True)
    comuna = forms.ModelChoiceField(queryset=Comuna.objects.none(), label="Comuna", required=True)
    image = forms.ImageField(label="Imagen de Perfil", required=False)

    class Meta:
        model = UserProfile
        fields = ['full_name', 'email', 'rut', 'date_of_birth', 'address', 'region', 'comuna', 'image']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['comuna'].queryset = Comuna.objects.filter(region_id=region_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['comuna'].queryset = Comuna.objects.none()
        elif self.instance.pk and self.instance.region:
            self.fields['comuna'].queryset = Comuna.objects.filter(region=self.instance.region).order_by('nombre')
        else:
            self.fields['comuna'].queryset = Comuna.objects.none()

    def save(self, commit=True):
        data = self.cleaned_data
        user = User(
            username=data['rut'],
            first_name=data['full_name'],
            email=data['email'],
            password=make_password(data['password']),
        )
        if commit:
            user.save()
            profile = super().save(commit=False)
            profile.user = user
            profile.region = data['region']
            profile.comuna = data['comuna']
            profile.save()
        return user



class EditProfileForm(forms.ModelForm):
    full_name = forms.CharField(label="Nombre Completo", max_length=100)
    email = forms.EmailField(label="Correo Electrónico", validators=[validate_email])
    address = forms.CharField(label="Dirección", max_length=300)
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        label="Región",
        required=False,
        empty_label="Seleccione una región"
    )
    comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.none(),
        label="Comuna",
        required=False,
        empty_label="Seleccione una comuna"
    )

    class Meta:
        model = UserProfile
        fields = ['address', 'region', 'comuna']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EditProfileForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['full_name'].initial = user.get_full_name()
            self.fields['email'].initial = user.email

            if hasattr(user, 'userprofile'):
                self.fields['region'].initial = user.userprofile.region
                self.fields['comuna'].initial = user.userprofile.comuna
                self.fields['comuna'].queryset = Comuna.objects.filter(region=user.userprofile.region)

        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['comuna'].queryset = Comuna.objects.filter(region_id=region_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['comuna'].queryset = Comuna.objects.none()

    def save(self, user, commit=True):
        user.first_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = super().save(commit=False)
            profile.user = user
            profile.address = self.cleaned_data['address']
            profile.region = self.cleaned_data['region']
            profile.comuna = self.cleaned_data['comuna']
            profile.save()
        return user
    
class CrearUsuarioForm(forms.Form):
    rut = forms.CharField(max_length=20, validators=[validar_rut_chileno])
    nombre = forms.CharField(max_length=100)
    email = forms.EmailField(label="Correo electrónico")
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(max_length=200, required=True)
    region = forms.ChoiceField(choices=[], required=True)
    comuna = forms.ChoiceField(choices=[], required=True)
    image = forms.ImageField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, validators=[validar_password_segura])

    def __init__(self, *args, **kwargs):
        regiones = kwargs.pop('regiones', [])
        comunas = kwargs.pop('comunas', [])
        super().__init__(*args, **kwargs)
        self.fields['region'].choices = [(r.id, r.nombre) for r in regiones]
        self.fields['comuna'].choices = [(c.id, c.nombre) for c in comunas]



class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha', 'motivo']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        if fecha < timezone.now():
            raise forms.ValidationError("No se puede agendar una fecha pasada.")
        return fecha
    
def validar_fecha_cita(fecha):
    
    if fecha.weekday() > 4:  
        raise ValidationError('Solo se pueden agendar citas de lunes a viernes.')
    
    
    if not (fecha.hour >= 10 and fecha.hour <= 17):
        raise ValidationError('La cita debe ser entre las 10:00 AM y las 5:00 PM.')

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha', 'motivo']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        
        
        if fecha < timezone.now():
            raise forms.ValidationError("No se puede agendar una fecha pasada.")
        
       
        validar_fecha_cita(fecha)
        
        return fecha