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

    def filtra_cliente__apelido(self):
        """
        filtra_cliente__apelido supõe:
        data_field na self.query = cliente__apelido
        form_field = cliente_apelido
        """
        cliente_apelido = (
            self.form.data['cliente_apelido']
            if 'cliente_apelido' in self.form.data
            else None
        )

        def do_filtra():
            self.query = self.query.filter(
                cliente__apelido = cliente_apelido)
            self.form.data['cliente_apelido'] = cliente_apelido

        if cliente_apelido:
            try:
                cliente = Cliente.objects.get(
                    apelido__iexact=cliente_apelido)
                cliente_apelido = cliente.apelido
                do_filtra()
            except Cliente.DoesNotExist as _:
                partes = cliente_apelido.split(' ')
                regex = r".*\s.*".join(partes)
                clientes = Cliente.objects.filter(
                    apelido__iregex=regex)
                if len(clientes) == 1:
                    cliente_apelido = clientes[0].apelido
                    do_filtra()
                    return

                if len(clientes) > 1:
                    qtd_lista_clientes = 10
                    apelidos = [
                        cliente.apelido
                        for cliente in clientes[:qtd_lista_clientes]
                    ]
                    if len(clientes) > qtd_lista_clientes:
                        apelidos.append('...')
                    msg_erro = (
                        "Mais de um cliente com apelido contendo "
                        f"'{cliente_apelido}' "
                        f"({', '.join(apelidos)})"
                    )
                else:
                    msg_erro = (
                        "Cliente com apelido contendo "
                        f"'{cliente_apelido}' não existe"
                    )
                self.form.errors['cliente_apelido'] = [msg_erro]
                raise StopStepsException("Filtro de cliente mal definido")

    def filtra_valor(self, data_field, form_field):
        valor = (
            self.form.data[form_field]
            if form_field in self.form.data
            else None
        )
        if valor:
            self.query = self.query.filter(
                **{data_field: valor}
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
