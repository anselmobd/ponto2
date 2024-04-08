from pprint import pprint

from django.db.models import Q
from django.db.models.signals import post_delete, pre_save, post_save, post_init
from django.dispatch import receiver

from bordado.models import Lancamento


def acerta_saldos_cliente(cliente, data):
    lancamento = Lancamento.objects.filter(
        Q(cliente=cliente) & Q(data__lt=data)
    ).order_by('-data', '-id').first()
    saldo = lancamento.saldo_cliente if lancamento else 0

    lancamentos = Lancamento.objects.filter(
        Q(cliente=cliente) & Q(data__gte=data)
    ).order_by('data', 'id')
    for lancamento in lancamentos:
        saldo += lancamento.valor
        if lancamento.saldo_cliente != saldo:
            lancamento.saldo_cliente = saldo
            lancamento.calculando = True
            lancamento.save()


def acerta_saldos_empresa(data):
    lancamento = Lancamento.objects.filter(
        Q(data__lt=data)
    ).order_by('-data', '-id').first()
    saldo = lancamento.saldo_empresa if lancamento else 0

    lancamentos = Lancamento.objects.filter(
        Q(data__gte=data)
    ).order_by('data', 'id')
    for lancamento in lancamentos:
        saldo += lancamento.valor
        if lancamento.saldo_empresa != saldo:
            lancamento.saldo_empresa = saldo
            lancamento.calculando = True
            lancamento.save()


@receiver(post_delete, sender=Lancamento)
def post_delete_lancamento(sender, instance, *args, **kwargs):
    cliente=instance.cliente
    data=instance.data
    acerta_saldos_cliente(cliente, data)
    acerta_saldos_empresa(data)


@receiver(pre_save, sender=Lancamento)
def pre_save_lancamento(sender, instance, *args, **kwargs):
    instance.propagar = not instance.calculando
    instance.calculando = False
    if instance.propagar:
        instance.busca_cliente = instance.cliente
        instance.busca_data = instance.data
        if instance.id:
            try:
                old_instance = Lancamento.objects.get(id=instance.id)
                instance.busca_data = min(
                    instance.busca_data, old_instance.data)
            except Lancamento.DoesNotExist:
                pass


@receiver(post_save, sender=Lancamento)
def post_save_lancamento(sender, instance, *args, **kwargs):
    if instance.propagar:
        acerta_saldos_cliente(instance.busca_cliente, instance.busca_data)
        acerta_saldos_empresa(instance.busca_data)


# @receiver(post_init, sender=Lancamento)
# def post_init_lancamento(sender, instance, *args, **kwargs):
#     if instance.cobranca:
#         informacao_list = []
#         if instance.cobranca.nf:
#             informacao_list.append(
#                 f"{instance.cobranca.tipo} {instance.cobranca.nf}")
#         else:
#             informacao_list.append(instance.cobranca.tipo)
#         informacao_list.append(f"Cobrança {instance.cobranca.id}")
#         if instance.n_parcelas > 1:
#             informacao_list.append(f"parcela {instance.parcela}/{instance.n_parcelas}")
#         informacao = "; ".join(informacao_list)
#         instance.informacao = informacao
