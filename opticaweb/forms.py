from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.hashers import make_password

class UserProfileForm(forms.ModelForm):
    full_name = forms.CharField(label="Nombre Completo")
    rut = forms.CharField(label="RUT", help_text="Formato: 12.345.678-9")
    email = forms.EmailField(label="Correo Electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", min_length=8)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha de nacimiento")
    address = forms.CharField(label="Dirección")
    image = forms.ImageField(label="Imagen de Perfil", required=False)

    class Meta:
        model = UserProfile
        fields = ['full_name', 'email', 'rut', 'date_of_birth', 'address', 'image']

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
            profile.save()
        return user
