import datetime
import re
import yaml
from pprint import pprint

from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaulttags import register
from django.db.models import Min
from django.utils.timezone import utc

from o2lib.strings import join2
from o2lib.utilitario import coalesce
from o2lib.yaml_obj import YamlUser


def request_user(request):
    user = None
    if request.user.is_authenticated:
        user = request.user
    return user


def get_empresa(request):
    if 'agator' in request.get_host():
        return 'agator'
    return 'tussor'


def is_alternativa(request):
    return request.get_host().startswith('alter')


def has_permission(request, permission):
    can = False
    user = request_user(request)
    if user:
        can = user.has_perm(permission)
    return can


def config_get_typed_value(config):
    type = config.parametro.tipo.codigo
    if type == 'SN':
        return config.valor
    if type == 'I':
        try:
            return int(config.valor)
        except Exception:
            pass
    return None


def rec_trac_log_to_dict(log, log_version=1):
    if log_version == 1:
        log = log.replace("<UTC>", "utc")
        log = re.sub(
            r'^(.*)<DstTzInfo \'America/Sao_Paulo\' -03-1 day, '
            r'21:00:00 STD>(.*)$',
            r'\1utc\2', log)
        log = re.sub(
            r'^(.*)<SimpleLazyObject: <User: ([^\s]*)>>(.*)$',
            r'\1"\2"\3', log)
        log = re.sub(
            r'^(.*)<User: ([^\s]*)>(.*)$',
            r'\1"\2"\3', log)
        dic = eval(log)
    elif log_version == 2:
        dic = yaml.load(log, Loader=yaml.Loader)
        for key in dic:
            if isinstance(dic[key], YamlUser):
                dic[key] = dic[key].object_instance
            if isinstance(dic[key], datetime.datetime):
                dic[key] = dic[key].replace(tzinfo=utc)
    return dic


def log_version_by_table(table):
    table_dict = {
        'Lote': 2,
        'SolicitaLote': 2,
        'NfEntrada': 2,
    }
    return table_dict.get(table, 1)


def dict_to_rec_trac_log(dic, log_version=1):
    if log_version == 1:
        return dic
    elif log_version == 2:
        for key in dic:
            if isinstance(dic[key], User):
                dic[key] = YamlUser(dic[key])
        return yaml.dump(dic)
