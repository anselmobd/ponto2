from pprint import pprint

from o2lib.views.base.exception import (
    StopStepsException,
)

from bordado.models import (
    Cliente,
)

__all__ = ['FiltroParaView']


class FiltroParaView():
    """
    FiltroParaView define métodos de filtros que pressupõem existencia de algos atributos:

    self.query: A query a ser filtrada
    self.form: O form da view
    """

    def _value_from_form(self, form_field):
        return (
            self.form.data[form_field]
            if form_field in self.form.data
            else None
        )

    def filtra_cliente__apelido(
            self,
            data_field='cliente__apelido',
            form_field='cliente_apelido',
            query_attr='query',
            apenas_um=True):
        """
        defaults:
            data_field em self.query = cliente__apelido
            form_field em self.form.data = cliente_apelido
            query_attr em self = query
        """
        apelido = self._value_from_form(form_field)

        def do_filtra():
            setattr(self, query_attr,
                getattr(self, query_attr).filter(
                    **{data_field: apelido}
                )
            )
            self.form.data[form_field] = apelido

        if apelido:
            try:
                cliente = Cliente.objects.get(
                    apelido__iexact=apelido)
                apelido = cliente.apelido
                exato = True
            except Cliente.DoesNotExist as _:
                try:
                    cliente = Cliente.objects.get(
                        apelido_slug__iexact=apelido)
                    apelido = cliente.apelido
                    exato = True
                except Cliente.DoesNotExist as _:
                    exato = False
            if exato:
                do_filtra()
            else:
                partes = apelido.split(' ')
                regex = r".*\s.*".join(partes)
                clientes = Cliente.objects.filter(
                    apelido__iregex=regex)
                if len(clientes) == 1:
                    apelido = clientes[0].apelido
                    do_filtra()
                    return

                msg_erro = ''
                if not clientes:
                    msg_erro = (
                        "Cliente com apelido contendo "
                        f"'{apelido}' não existe"
                    )
                elif apenas_um:
                    qtd_lista_clientes = 10
                    apelidos = [
                        cliente.apelido
                        for cliente in clientes[:qtd_lista_clientes]
                    ]
                    if len(clientes) > qtd_lista_clientes:
                        apelidos.append('...')
                    msg_erro = (
                        "Mais de um cliente com apelido contendo "
                        f"'{apelido}' "
                        f"({', '.join(apelidos)})"
                    )
                else:
                    setattr(self, query_attr,
                        getattr(self, query_attr).filter(
                            **{f'{data_field}__icontains': apelido}
                        )
                    )

                if msg_erro:
                    self.form.errors[form_field] = [msg_erro]
                    raise StopStepsException("Filtro de cliente mal definido")

    def filtra_valor(self, data_field, form_field):
        valor = self._value_from_form(form_field)
        if valor:
            self.query = self.query.filter(
                **{data_field: valor}
            )

    def filtra_icontains(self, data_field, form_field):
        valor = (
            self.form.data[form_field]
            if form_field in self.form.data
            else None
        )
        if valor:
            self.query = self.query.filter(
                **{f'{data_field}__icontains': valor}
            )

    def filtra_valor_de_ate(self, data_field, form_field_de, form_field_ate):
        valor_de = (
            self.form.data[form_field_de]
            if form_field_de in self.form.data
            else None
        )
        valor_ate = (
            self.form.data[form_field_ate]
            if form_field_ate in self.form.data
            else None
        )
        if valor_de or valor_ate:
            if valor_de == valor_ate:
                self.query = self.query.filter(
                    **{data_field: valor_de}
                )
                return
            if valor_de:
                self.query = self.query.filter(
                    **{f"{data_field}__gte": valor_de}
                )
            if valor_ate:
                self.query = self.query.filter(
                    **{f"{data_field}__lte": valor_ate}
                )
