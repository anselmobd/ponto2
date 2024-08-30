from pprint import pprint
from datetime import (
    datetime,
    timezone,
    timedelta,
)

from django.utils.timezone import localtime


__dow_info = {
    0: {'name': 'segunda-feira', 'plural': 'segundas-feiras',
        'alias': 'segunda', 'abb': 'seg'},
    1: {'name': 'terça-feira', 'plural': 'terças-feiras',
        'alias': 'terça', 'abb': 'ter'},
    2: {'name': 'quarta-feira', 'plural': 'quartas-feiras',
        'alias': 'quarta', 'abb': 'qua'},
    3: {'name': 'quinta-feira', 'plural': 'quintas-feiras',
        'alias': 'quinta', 'abb': 'qui'},
    4: {'name': 'sexta-feira', 'plural': 'sextas-feiras',
        'alias': 'sexta', 'abb': 'sex'},
    5: {'name': 'sábado', 'plural': 'sábados',
        'alias': 'sábado', 'abb': 'sab'},
    6: {'name': 'domingo', 'plural': 'domingos',
        'alias': 'domingo', 'abb': 'dom'},
}


def utc_now():
    """Return datetime with time zone UTC"""
    return datetime.now(timezone.utc)


def tz_now():
    """Return datetime with time zone based in Django TZ"""
    return localtime()


def tz_today():
    """Return date today considering TZ"""
    return tz_now().date()


def tz_yesterday():
    """Return date yesterday considering TZ"""
    return (tz_today() - timedelta(days=1))


def dow_info(dt, info, capitalize=False):
    dow = dt.weekday()
    result = __dow_info[dow][info]
    if capitalize:
        return result.capitalize()
    return result


def ymd(data):
    """Return data in format YYYY-MM-DD"""
    return f"{data:%Y-%m-%d}"


def today_ymd():
    """Return today in format YYYY-MM-DD"""
    return ymd(tz_today())


def yesterday_ymd():
    """Return yesterday in format YYYY-MM-DD"""
    return ymd(tz_yesterday())


def dmy(data):
    """Return data in format DD/MM/YYYY"""
    return f"{data:%d/%m/%Y}"


def dmy_or_empty(data):
    """Return dmy or empty"""
    return dmy(data) if data else ''


def strdmy2date(text):
    """Convert string in format DD/MM/YYYY to date"""
    return datetime.strptime(text, '%d/%m/%Y').date()


def strymd2date(text):
    """Convert string in format YYYY-MM-DD to date"""
    return datetime.strptime(text, '%Y-%m-%d').date()


def ano_atual():
    """Return year of today, considering TZ"""
    hoje = tz_today()
    return hoje.year


def mes_atual():
    """Return month of today, considering TZ"""
    hoje = tz_today()
    return hoje.month


def dia_atual():
    """Return day of today, considering TZ"""
    hoje = tz_today()
    return hoje.day


def yesterday(dt):
    """Return date yesterday from date dt"""
    return (dt - timedelta(days=1))
