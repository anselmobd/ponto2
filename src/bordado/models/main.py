from o2lib.models.base import logged_user

from bordado.models.aponta_prod import ApontamentoProducao
from bordado.models.bordado import Bordado
from bordado.models.cliente import Cliente
from bordado.models.cobranca import Cobranca
from bordado.models.contato import Contato
from bordado.models.dificuldade_bordado import DificuldadeBordado
from bordado.models.forma_pagamento import (
    FormaPagamento,
    forma_pagamento_default_id,
)
from bordado.models.op import OrdemProducao
from bordado.models.pedido import Pedido
from bordado.models.lancamento import Lancamento
from bordado.models.pedido_item import PedidoItem
from bordado.models.pedido_item_cobranca import PedidoItemCobranca
from bordado.models.tipo_comunicacao import (
    TipoComunicacao,
    tipo_comunicacao_default_id,
)


__all__ = [
    'ApontamentoProducao',
    'Bordado',
    'Cliente',
    'Cobranca',
    'Contato',
    'DificuldadeBordado',
    'FormaPagamento',
    'forma_pagamento_default_id',
    'Lancamento',
    'logged_user',
    'OrdemProducao',
    'Pedido',
    'PedidoItem',
    'PedidoItemCobranca',
    'TipoComunicacao',
    'tipo_comunicacao_default_id',
]


# class Empresa(models.Model):
#     nome = models.CharField(
#         max_length=50,
#         unique=True,
#     )

#     def __str__(self):
#         return f"{self.nome}"

#     class Meta:
#         db_table = 'po2_empresa'
#         verbose_name = "Empresa"
#         ordering = ['nome']
