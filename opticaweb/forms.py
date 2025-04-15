from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    # Campos adicionales
    full_name = forms.CharField(max_length=255, label="Nombre Completo")
    rut = forms.CharField(max_length=12, label="RUT", help_text="Formato: 12.345.678-9")
    email = forms.EmailField(label="Correo Electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", min_length=8)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha de Nacimiento")
    address = forms.CharField(max_length=255, label="Dirección")
    
    class Meta:
        model = UserProfile

        fields = ['full_name', 'rut', 'email', 'password', 'date_of_birth', 'address']