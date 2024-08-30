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
        self.form_cookie_per_user = True
        self.form_cookie_prefix = ''

        # internals
        self._copy_form_data = True

    def do_copy_form_data(self):
        if self._copy_form_data:
            self.form.data = dict(self.form.data)
            self._copy_form_data = False

    def set_form_data(self, field, value):
        self.do_copy_form_data()
        self.form.data[field] = value

    def do_cleaned_data2(self):
        for field in self.form.cleaned_data:
            value = self.form.cleaned_data[field]
            if self.cleaned_data2self:
                setattr(self, field, value)
            if self.cleaned_data2context:
                self.context[field] = value
            if self.cleaned_data2data:
                self.set_form_data(field, value)

    def cookie_name(self, field):
        parts = [field]
        if self.form_cookie_prefix:
            parts.append(self.form_cookie_prefix)
        if self.form_cookie_per_user and self.request.user:
            parts.append(str(self.request.user))
        return '.'.join(parts[::-1])

    def form_to_cookies(self):
        if not hasattr(self.Form_class, 'cookie_field'):
            return
        for field in self.Form_class.cookie_field:
            self.set_del_cookies[
                self.cookie_name(field)
            ] = self.form.cleaned_data[field]

    def render_mount(self):
        self.pre_mount_context()
        if self.form.is_valid():
            self.do_cleaned_data2()
            self.mount_context()
            self.form_to_cookies()
        self.context['form'] = self.form
        self.post_mount_context()
        return self.get_response_with_cookies()

    def set_form_arg(self, field):
        value = self.get_arg(field)
        if value is not None:
            self.set_form_data(field, value)

    def form_fields_none(self):
        """Monta um dict com todos os campos do Form_class
        e valores None"""
        return {name: None for name in self.Form_class.base_fields}

    def form_fields_initials(self):
        """Monta um dict com campos do Form_class que têm inicial
        e os valores de initial"""
        return {
            name: field.initial
            for name, field in self.Form_class.base_fields.items()
            if field.initial is not None
        }

    def pre_form(self):
        pass

    def cookies_to_form_dict_initial(self):
        if not hasattr(self.Form_class, 'cookie_field'):
            return
        for field in self.Form_class.cookie_field:
            if self.cookie_name(field) in self.request.COOKIES:
                self.form_dict_initial[field] = (
                    self.request.COOKIES.get(self.cookie_name(field))
                )

    def init_kwargs_to_post(self, kwargs):
            set_values = self.form_fields_initials()
            set_values.update(self.form_dict_initial)
            if set_values:
                for key, value in set_values.items():
                    kwargs[key] = value
                    self.get_args.append(key)

    def get(self, request, *args, **kwargs):
        self.init_self(request, **kwargs)

        call_post = False

        if self.get_args2form:
            for arg in self.get_args:
                if self.get_arg(arg) is not None:
                    call_post = True

        if self.get_vars2form:
            if request.GET:
                call_post = True

        self.cookies_to_form_dict_initial()
        if call_post:
            self.init_kwargs_to_post(kwargs)

        if self.get_vars2form:
            if request.GET:
                for key, value in dict(request.GET).items():
                    kwargs[key] = value[0]
                    self.get_args.append(key)

        if call_post:
            return self.post(request, *args, **kwargs)

        self.pre_form()
        if self.form_class_has_initial:
            self.form = self.Form_class(
                initial=self.form_dict_initial, **self.form_create_kwargs)
        else:
            self.form = self.Form_class(
                initial=self.form_fields_none(), **self.form_create_kwargs)

        self.context['form_method'] = 'GET'
        return self.render_mount()

    def post(self, request, *args, **kwargs):
        self.init_self(request, **kwargs)

        self.pre_form()
        self.form = self.Form_class(
            self.request.POST, **self.form_create_kwargs)

        if self.get_args2form:
            for arg in self.get_args:
                self.set_form_arg(arg)

        self.context['form_method'] = 'POST'
        return self.render_mount()
