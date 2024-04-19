from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.urls import reverse

from o2lib.views.base.get_post import O2BaseGetPostView

from bordado.forms import FinanceiroForm
from bordado.models import Pedido


class Financeiro(LoginRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super().__init__()
        self.Form_class = FinanceiroForm
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/financeiro.html'
        self.title_name = 'Financeiro'

    def mount_context(self):
        if self.pedido_numero:
            try:
                pedido = Pedido.objects.get(numero=self.pedido_numero)
            except Pedido.DoesNotExist:
                pedido = None
