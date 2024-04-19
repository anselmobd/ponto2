from pprint import pprint

from django.shortcuts import redirect, render


__all__ = ['index']


def index_puro(request):
    # return redirect('bordado:index')
    return render(request, 'principal_p.html', {})
