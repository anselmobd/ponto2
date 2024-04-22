from pprint import pprint

from django.apps import apps
from django.shortcuts import redirect, render
from django.views import View

from o2lib.views.base.steps import Steps

__all__ = ['CustomView']



class CustomView(View):
    """
    Base para customizar views

    """

    def __init__(self, *args, **kwargs):
        """
        Inicializa parâmetros:
        get_args
            Lista de nomes de variáveis recebidas por GET.
        get_args2context
            Boolean indicando se as variáveis recebidas por GET vão para o
            context.
        get_args2self
            Boolean indicando se as variáveis recebidas por GET vão para o
            self da view.
        redirect
            String ou tupla que serão attibutos da execução de um redirect.
            Caso None, é executado um render.
        # error_field
        #     Nome da chave do context que guarda lista de mensagens de erro
        #     recebidas pelo método do_steps.
        """
        super().__init__(*args, **kwargs)
        self.get_args = []
        self.get_args2context = False
        self.get_args2self = False
        self.redirect = None

        self.context = {'error_msgs': []}

        # self.steps = Steps(self)

    def init_self(self, request, **kwargs):
        """
        Inicializa variáveis do self:
            request
            kwargs
            context
            {outras, caso get_args2self}
        """
        self.request = request
        self.kwargs = kwargs

        self.app_name = request.resolver_match.app_name
        if self.app_name == 'producao':
            self.app_name = 'lotes'
        self.app_config = apps.get_app_config(self.app_name)
        self.context.update({'app_config': self.app_config})

        if hasattr(self, 'title_name'):
            self.context.update({'titulo': self.title_name})

        if self.get_args2context:
            for arg in self.get_args:
                arg_value = self.get_arg(arg)
                self.context.update({arg: arg_value})

        if self.get_args2self:
            for arg in self.get_args:
                arg_value = self.get_arg(arg)
                setattr(self, arg, arg_value)

    def get_arg(self, field):
        """
        Retorna Keyword Argument ou nulo
        """
        return self.kwargs[field] if field in self.kwargs else None

    def render_or_redirect(self):
        """
        Se self.redirect for definido, execute redirect.
        Senão, execute render com request, template_name e context
        """
        if self.redirect:
            if not isinstance(self.redirect, tuple):
                self.redirect = (self.redirect, )
            return redirect(*self.redirect)
        return render(self.request, self.template_name, self.context)

    def pre_mount_context(self):
        """
        Metodo de pré-montagem de contexto
        """
        pass

    def mount_context(self):
        """
        Metodo de montagem de contexto
        """
        pass
