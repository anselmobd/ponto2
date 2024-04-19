from pprint import pprint

from django.shortcuts import redirect, render


__all__ = ['index', 'sobre']


def index_vue(request):
    if request.user.is_authenticated:
        return render(request, 'bordado/index/main.html', {})
    else:
        return redirect('index')


def sobre(request):
    return render(request, 'bordado/sobre.html', {})


def index(request):
    if request.user.is_authenticated:
        return render(request, 'bordado/index.html', {})
    else:
        return redirect('index')
