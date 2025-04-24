
from django.urls import path
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password


@api_view(['POST'])
def login_api(request):
    data = JSONParser().parse(request)  
    
    username = data['username']
    password = data['password']
    
    try:
        user = User.objects.get(username=username)  
    except User.DoesNotExist:
        return Response("Usuario incorrecto")  
    
    pass_valido = check_password(password, user.password)  
    if not pass_valido:
        return Response("Contraseña incorrecta")  
    
    token, created = Token.objects.get_or_create(user=user)  
    return Response(token.key)  