from django.shortcuts import redirect
from functools import wraps

def solo_admin(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('admin_user_rol') != 'administrador':
            return redirect('panel_colaborador')
        return view_func(request, *args, **kwargs)
    return wrapper

def solo_colaborador(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('admin_user_rol') != 'colaborador':
            return redirect('panel_administrador')
        return view_func(request, *args, **kwargs)
    return wrapper
