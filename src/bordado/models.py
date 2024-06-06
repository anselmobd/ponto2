from pprint import pprint

from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from o2lib.classes.logged_in_user import SingletonLoggedInUser
from o2lib.codes.cnpj import CNPJ
from o2lib.datetime.tz import tz_local


__all__ = [
    'ApontamentoProducao',
    'Bordado',
    'Cliente',
    'Cobranca',
    'DificuldadeBordado',
    'Lancamento',
    'OrdemProducao',
    'Pedido',
    'PedidoItem',
    'PedidoItemCobranca',
    'TipoComunicacao',
]


def logged_user():
    return SingletonLoggedInUser().user


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


class TipoComunicacao(models.Model):
    admin_order = 50
    descricao = models.CharField(
        "Descrição",
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = 'po2_tipo_comunicacao'
        verbose_name = "Tipo de comunicação"
        verbose_name_plural = "Tipos de comunicação"
        ordering = ['id']


def tipo_comunicacao_default_id():
    tipo_comunicacao = TipoComunicacao.objects.filter(descricao="Telefone").first()
    if tipo_comunicacao:
        return tipo_comunicacao.id
    return None


class FormaPagamento(models.Model):
    admin_order = 75
    nome = models.CharField(
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'po2_forma_pagamento'
        verbose_name = "Forma de pagamento"
        verbose_name_plural = "Formas de pagamento"
        ordering = ['id']


def forma_pagamento_default_id():
    forma_pagamento = FormaPagamento.objects.filter(nome="Boleto").first()
    if forma_pagamento:
        return forma_pagamento.id
    return None


class ClienteManager(models.Manager):
    def get_by_natural_key(self, cnpj9, cnpj4):
        return self.get(cnpj9=cnpj9, cnpj4=cnpj4)


class Cliente(models.Model):
    admin_order = 100
    # empresa = models.ForeignKey(
    #     Empresa,
    #     on_delete=models.PROTECT,
    # )
    nome = models.CharField(
        "Nome/Razão Social",
        max_length=100,
        blank=True,
    )
    fansasia = models.CharField(
        "Nome Fantasia",
        max_length=100,
        blank=True,
    )
    apelido = models.CharField(
        max_length=30,
        unique=True,
    )
    apelido_slug = models.SlugField(
        max_length=30,
        # unique=True,
        blank=True,
        null=True,
    )
    cnpj9 = models.PositiveIntegerField(
        "CNPJ (raiz)",
        default=None,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(999_999_999)],
    )
    cnpj4 = models.PositiveSmallIntegerField(
        "CNPJ (filial)",
        default=None,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(9_999)],
    )
    cnpj2 = models.PositiveSmallIntegerField(
        "CNPJ (dígitos)",
        default=None,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(99)],
    )
    cep = models.CharField(
        "CEP",
        max_length=10,
        blank=True,
    )
    logradouro = models.CharField(
        max_length=100,
        blank=True,
    )
    numero = models.PositiveSmallIntegerField(
        "Número",
        default=None,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(999_999)],
    )
    complemento = models.CharField(
        max_length=30,
        blank=True,
    )
    bairro = models.CharField(
        max_length=100,
        blank=True,
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
    )
    uf = models.CharField(
        max_length=2,
        blank=True,
    )
    comunicacao = models.ForeignKey(
        TipoComunicacao,
        default=tipo_comunicacao_default_id,
        on_delete=models.PROTECT,
        verbose_name="Comunicação preferêncial",
    )
    conta_corrente = models.BooleanField(
        "Financeiro tipo conta corrente?",
        default=False,
    )
    parcelamento = models.CharField(
        "Parcelamento padrão",
        max_length=30,
        default="",
        blank=True,
    )
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        on_delete=models.PROTECT,
        verbose_name="Forma de pagamento",
        default=forma_pagamento_default_id,
    )
    nf = models.BooleanField(
        "Nota Fiscal por cobrança?",
        default=True,
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="usuário",
        default=logged_user,
    )
    quando = models.DateTimeField(auto_now=True)

    objects = ClienteManager()

    @property
    def cnpj(self):
        if ( self.cnpj9 is not None
            and self.cnpj4 is not None
            and self.cnpj2 is not None
        ):
            cnpj = CNPJ(self.cnpj9, self.cnpj4, self.cnpj2)
            mark = "" if cnpj.valid() else "!"
            return f"{cnpj}{mark}"
        else:
            return "!"

    def __str__(self):
        return self.apelido_slug

    def save(self, *args, **kwargs):
        self.apelido_slug = slugify(self.apelido)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'po2_cliente'
        verbose_name = "Cliente"
        ordering = ['apelido']
        # unique_together = [['cnpj9', 'cnpj4']]

    def natural_key(self):
        return (self.cnpj9, self.cnpj4)

    @staticmethod
    def nullable_natural_key(cliente):
        return (None, None) if cliente is None else cliente.natural_key()

    @staticmethod
    def default_client_id():
        return Cliente.objects.first().id


class Contato(models.Model):
    admin_order = 150
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    nome = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    telefone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        "E-mail",
        blank=True,
        null=True,
    )
    preferencial = models.BooleanField(
        default=False,
    )

    def __str__(self):
        id = self.nome or self.email or self.telefone or "Vazio!"
        return f"({self.cliente.nome}) {id}"

    def save(self, *args, **kwargs):
        id = self.id if self.id else -1
        outros = Contato.objects.filter(cliente=self.cliente).exclude(id=id)
        if self.preferencial:
            if outros:
                for outro in outros:
                    outro.preferencial = False
                    outro.save()
        else:
            if not outros:
                self.preferencial = True
        super(Contato, self).save(*args, **kwargs)

    class Meta:
        db_table = 'po2_contato'
        verbose_name = "Contato"


class DificuldadeBordadoManager(models.Manager):
    def get_by_natural_key(self, ordem):
        return self.get(ordem=ordem)


class DificuldadeBordado(models.Model):
    admin_order = 200
    ordem = models.PositiveSmallIntegerField(
        unique=True,
    )
    descricao = models.CharField(
        "Descrição",
        max_length=50,
        unique=True,
    )

    objects = DificuldadeBordadoManager()

    def id_indefinida():
        return DificuldadeBordado.objects.get(ordem=0).id

    def __str__(self):
        return f"{self.ordem}-{self.descricao}"

    class Meta:
        db_table = 'po2_dificuldade_bordado'
        verbose_name = "Dificuldade de bordado"
        verbose_name_plural = "Dificuldades de bordado"
        ordering = ['ordem']

    def natural_key(self):
        return (self.ordem, )


class BordadoManager(models.Manager):
    def get_by_natural_key(self, nome, codigo, cnpj9, cnpj4):
        return self.get(
            nome=nome, codigo=codigo, cliente__cnpj9=cnpj9, cliente__cnpj4=cnpj4)


class Bordado(models.Model):
    admin_order = 300
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    nome = models.CharField(
        max_length=50,
    )
    codigo = models.CharField(
        "código",
        max_length=50,
        default="",
        blank=True,
        null=True,
    )
    pontos = models.PositiveIntegerField(
        default=0,
    )
    cores = models.PositiveIntegerField(
        default=0,
    )
    tamanho_maximo = models.PositiveIntegerField(
        "tamanho máximo",
        default=0,
        help_text="em milímetros",
    )
    dificuldade = models.ForeignKey(
        DificuldadeBordado,
        on_delete=models.PROTECT,
        default=DificuldadeBordado.id_indefinida,
    )

    objects = BordadoManager()

    def __str__(self):
        cliente = f" - {self.cliente}" if self.cliente else ""
        codigo = f" - {self.codigo}" if self.codigo else ""
        return f"{self.nome}{codigo}{cliente}"

    class Meta:
        db_table = 'po2_bordado'
        verbose_name = "Bordado"
        ordering = ['nome', 'codigo']
        unique_together = [['nome', 'codigo', 'cliente']]

    def natural_key(self):
        return (self.nome, self.codigo) + Cliente.nullable_natural_key(self.cliente)

    natural_key.dependencies = ['bordado.cliente']


class Pedido(models.Model):
    admin_order = 400
    numero = models.AutoField(
        "Número",
        primary_key=True
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    inserido_em = models.DateTimeField(auto_now_add=True)
    entrega = models.DateField(
        blank=True,
        null=True,
    )
    cancelado = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f"{self.numero:04d} - {self.cliente}"

    class Meta:
        db_table = 'po2_pedido'
        ordering = ['-numero']


class PedidoItemManager(models.Manager):
    def get_by_natural_key(self, ordem, pedido):
        return self.get(ordem=ordem, pedido__numero=pedido)


class PedidoItem(models.Model):
    admin_order = 500
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    ordem = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=0,
    )
    data_pedido = models.DateField(
        "Data do pedido",
        default=timezone.localdate
    )
    inserido_em = models.DateTimeField(auto_now_add=True)
    bordado = models.ForeignKey(
        Bordado,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1_000_000)],
        default=0,
    )
    preco = models.DecimalField(
        "Preço",
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(1_000_000)],
        default=0,
    )
    programacao = models.DecimalField(
        "Pogramação",
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(1_000_000)],
        default=0,
    )
    ajuste = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(-1_000), MaxValueValidator(1_000)],
        default=0,
    )
    cancelado = models.BooleanField(
        default=False,
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="usuário",
        default=logged_user,
    )

    objects = PedidoItemManager()

    @property
    def cliente(self):
        return self.pedido.cliente

    def __str__(self):
        return (
            f"{self.id}: {self.pedido.numero:04d}/{self.ordem} "
            f"{self.quantidade}*'{self.bordado}'"
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.ordem = (
                PedidoItem.objects.filter(pedido=self.pedido).count() + 1
            ) * 10
        super(PedidoItem, self).save(*args, **kwargs)

    class Meta:
        db_table = 'po2_pedido_item'
        verbose_name = "Item de pedido"
        verbose_name_plural = "Itens de pedido"
        ordering = ['-pedido__numero', '-ordem']
        unique_together = [['ordem', 'pedido']]

    def natural_key(self):
        return (self.ordem, self.pedido.numero)

    natural_key.dependencies = ['bordado.pedido']


class Cobranca(models.Model):
    admin_order = 700
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
    )
    valor = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(1_000_000)],
        default=0,
    )
    informacao = models.CharField(
        max_length=50,
        default="",
        blank=True,
        null=True,
    )
    comunicacao = models.ForeignKey(
        TipoComunicacao,
        on_delete=models.PROTECT,
    )
    nf = models.PositiveIntegerField(
        "NF",
        blank=True,
        null=True,
    )
    data = models.DateField(
    )
    parcelamento = models.CharField(
        max_length=50,
        default="0",
        blank=True,
        null=True,
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="usuário",
        default=logged_user,
    )
    quando = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        nf = f" (NF {self.nf})" if self.nf else ""
        comunicacao = f" [{self.comunicacao.descricao}]" if self.comunicacao else ""
        return f"{self.id}: {self.informacao}{comunicacao}{nf} - {self.data}"

    class Meta:
        db_table = 'po2_cobranca'
        verbose_name = "Cobrança"
        ordering = ['-id']


class PedidoItemCobranca(models.Model):
    admin_order = 800
    pedido_item = models.ForeignKey(
        PedidoItem,
        on_delete=models.PROTECT,
        related_name='cobrancas',
        blank=False,
        null=False,
    )
    cobranca = models.ForeignKey(
        Cobranca,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    valor = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(1_000_000)],
        default=0,
    )

    class Meta:
        db_table = 'po2_pedido_item_cobranca'
        verbose_name = "Cobrança de item de pedido"
        verbose_name_plural = "Cobranças de itens de pedido"


class Lancamento(models.Model):
    admin_order = 900
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
    )
    data = models.DateField(
    )
    cobranca = models.ForeignKey(
        Cobranca,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    parcela = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    n_parcelas = models.PositiveSmallIntegerField(
        "Nº de parcelas",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    informacao = models.CharField(
        "Informação",
        max_length=50,
    )
    valor = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(-1_000_000), MaxValueValidator(1_000_000)],
        default=0,
    )
    calculando = models.BooleanField(
        default=False,
    )
    saldo_cliente = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(-1_000_000), MaxValueValidator(1_000_000)],
        default=0,
    )
    saldo_empresa = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(-1_000_000), MaxValueValidator(1_000_000)],
        default=0,
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="usuário",
        related_name='+',
        default=logged_user,
    )
    quando = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}: {self.data} {self.cliente}"

    class Meta:
        db_table = 'po2_lancamento'
        verbose_name = "Lançamento"
        ordering = ['-data', '-id']


class OrdemProducao(models.Model):
    admin_order = 1000
    numero = models.AutoField(
        "Número",
        primary_key=True
    )
    pedido_item = models.ForeignKey(
        PedidoItem,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1_000_000)],
        default=0,
    )
    cancelado = models.BooleanField(
        default=False,
    )
    inserido_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OP {self.numero:04d}; {self.pedido_item}"

    class Meta:
        db_table = 'po2_op'
        verbose_name = "Ordem de produção"
        verbose_name_plural = "Ordens de produção"
        ordering = ['-numero']


class ApontamentoProducaoManager(models.Manager):
    def get_by_natural_key(self, apontado_em, op):
        return self.get(apontado_em=apontado_em, op__numero=op)


class ApontamentoProducao(models.Model):
    admin_order = 1100
    op = models.ForeignKey(
        OrdemProducao,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    qtd_perda = models.IntegerField(
        "quantidade de perda",
        validators=[MinValueValidator(0), MaxValueValidator(1_000_000)],
        default=0,
    )
    qtd_prod = models.IntegerField(
        "quantidade produzida",
        validators=[MinValueValidator(0), MaxValueValidator(1_000_000)],
        default=0,
    )
    apontado_em = models.DateTimeField(auto_now_add=True)
    encerrado = models.BooleanField(
        default=False,
    )

    objects = ApontamentoProducaoManager()

    def __str__(self):
        return (
            f"OP {self.op.numero:04d} {self.qtd_prod} ({self.qtd_perda}) "
            f"{tz_local(self.apontado_em):%d/%m/%Y %H:%M:%S}"
        )
    class Meta:
        db_table = 'po2_aponta_prod'
        verbose_name = "Apontamento de produção"
        verbose_name_plural = "Apontamentos de produção"
        ordering = ['-op_id', 'apontado_em']
        unique_together = [['apontado_em', 'op']]

    def natural_key(self):
        return (self.apontado_em, self.op.numero)

    natural_key.dependencies = ['bordado.ordemproducao']
