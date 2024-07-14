from pprint import pprint

from o2lib.views.base.custom import CustomView


class O2BaseGetPostView(CustomView):
    """Classe base para uma view com GET e POST
    
    Obrigatório definir no __init__:
        Form_class <django.forms.Form>
    """

    def __init__(self, *args, **kwargs):
        """Inicializa parâmetros, sendo:
        
        cleaned_data2self
            valores no self.form.cleaned_data viram atributos do objeto (self)
        """
        super(O2BaseGetPostView, self).__init__(*args, **kwargs)
        self.Form_class = None
        self.form_class_has_initial = False
        self.form_dict_initial = {}
        self.form_create_kwargs = {}
        self.get_args2form = True
        self.get_vars2form = False
        self.cleaned_data2self = False
        self.cleaned_data2context = False
        self.cleaned_data2data = False

    def do_cleaned_data2self(self):
        if self.cleaned_data2self:
            for field in self.form.cleaned_data:
                setattr(self, field, self.form.cleaned_data[field])

    def do_cleaned_data2context(self):
        if self.cleaned_data2context:
            for field in self.form.cleaned_data:
                value = self.form.cleaned_data[field]
                self.context.update({field: value})

    def do_cleaned_data2data(self):
        if self.cleaned_data2data:
            self.form.data = dict(self.form.data)
            for field in self.form.cleaned_data:
                self.form.data[field] = self.form.cleaned_data[field]

    def render_mount(self):
        self.pre_mount_context()
        if self.form.is_valid():
            self.do_cleaned_data2self()
            self.do_cleaned_data2context()
            self.do_cleaned_data2data()
            self.mount_context()
        self.context['form'] = self.form
        return self.render_or_redirect()

    def set_form_arg(self, field):
        value = self.get_arg(field)
        if value is not None:

            # evita erro "This QueryDict instance is immutable"
            aux_data = self.form.data.copy()
            self.form.data = aux_data

            self.form.data[field] = value

    def empty_form_initial(self):
        """Monta um dict com campos do Form_class e valores None"""
        return {name: None for name in self.Form_class.base_fields}

    def form_initial(self):
        """Metodo chamado no GET para colocar valores no dict que inicializará o Form_class"""
        dict_initial = self.empty_form_initial()
        dict_initial.update(self.form_dict_initial)
        return dict_initial

    def pre_form(self):
        pass

    def get(self, request, *args, **kwargs):
        self.init_self(request, **kwargs)

        call_post = False
        if self.get_args2form:
            for arg in self.get_args:
                if self.get_arg(arg) is not None:
                    call_post = True
        if self.get_vars2form:
            if request.GET:
                for key, value in dict(request.GET).items():
                    kwargs[key] = value[0]
                    self.get_args.append(key)
                call_post = True
        if call_post:
            return self.post(request, *args, **kwargs)

        self.pre_form()
        if self.form_class_has_initial:
            self.form = self.Form_class(**self.form_create_kwargs)
        else:
            self.form = self.Form_class(
                initial=self.form_initial(), **self.form_create_kwargs)
        self.context['form_method'] = 'GET'
        return self.render_mount()

    def post(self, request, *args, **kwargs):
        self.init_self(request, **kwargs)
        self.pre_form()
        self.form = self.Form_class(self.request.POST, **self.form_create_kwargs)

        if self.get_args2form:
            for arg in self.get_args:
                self.set_form_arg(arg)

        self.context['form_method'] = 'POST'
        return self.render_mount()
