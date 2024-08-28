from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.views.base.get_post import O2BaseGetPostView

from bordado.forms.financeiro.mes import FinanceiroMesForm
from bordado.views.base.filtro import FiltroParaView


__all__ = ['FinanceiroMesView']


class FinanceiroMesView(
        LoginRequiredMixin, O2BaseGetPostView, FiltroParaView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = FinanceiroMesForm
        self.template_name = "bordado/financeiro/mes.html"
        self.title_name = "Financeiro - Mês"
