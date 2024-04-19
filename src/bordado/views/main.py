from pprint import pprint

from django.shortcuts import redirect, render


__all__ = ['index', 'sobre', 'menu']


def index(request):
    if request.user.is_authenticated:
        return render(request, 'bordado/index/main.html', {})
    else:
        return redirect('bordado:sobre')


def sobre(request):
    return render(request, 'bordado/sobre.html', {})


def sobre_puro(request):
    return render(request, 'bordado/sobre_p.html', {})


def menu(request):
    return render(request, 'bordado/menu.html', {})


def menu_puro(request):
    if request.user.is_authenticated:
        return render(request, 'bordado/menu_p.html', {})
    else:
        return redirect('bordado:sobre_p')
