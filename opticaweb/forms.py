from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Region, Comuna
from django.contrib.auth.hashers import make_password
from .models import Cita
from django.utils import timezone

class UserProfileForm(forms.ModelForm):
    full_name = forms.CharField(label="Nombre Completo")
    rut = forms.CharField(label="RUT", help_text="Formato: 12.345.678-9")
    email = forms.EmailField(label="Correo Electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", min_length=8)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha de nacimiento")
    address = forms.CharField(label="Dirección")
    region = forms.ModelChoiceField(queryset=Region.objects.all(), label="Región", required=False)
    comuna = forms.ModelChoiceField(queryset=Comuna.objects.none(), label="Comuna", required=False)
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
    email = forms.EmailField(label="Correo Electrónico")
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
