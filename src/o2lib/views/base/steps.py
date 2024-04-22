from pprint import pprint

from django.views import View
from django.forms import Form
from django.forms.utils import ErrorList

from o2lib.views.base.exception import (
    StepErrorException,
    StopStepsException, 
)

__all__ = ['Steps']


class Steps():
    """
    Base para método "do steps"

    """

    def __init__(self,
            instance, context_field='context', error_field='msg_error'):
        """
        Inicializa parâmetros:
        context
            dict de dados
        error_field
            Nome da chave do context que guarda lista de mensagens de erro
            recebidas pelo método do_steps.
        """
        self.instance = instance
        self.error_field = error_field
        self.context_field = context_field

    def add_error_field_msg(self, error_field, message, force_init=False):
        context = self.get_attr_value(
            self.instance, self.context_field, value=[])
        if force_init or error_field not in context:
            context[error_field] = []
        context[error_field].append(message)

    def get_step_definition(self, step):
        storage_location = ''
        error_field = self.error_field
        if isinstance(step, tuple):
            if isinstance(step[0], str):
                storage_location = step[0]
                next_values = step[1:]
            execute = next_values[0]
            if len(next_values) > 1:
                error_field = next_values[1]
        else:
            execute = step
        return storage_location, execute, error_field

    def get_attr_value(self, instance, attr, value=None):
        if not hasattr(instance, attr):
            setattr(instance, attr, value)
        return getattr(instance, attr)

    def get_dict_value(self, dictio, key, value=None):
        if key not in dictio:
            dictio[key] = value
        return dictio[key]

    def location_keys(self, location):
        keys = location.split('.')
        if keys[0] == '':
            keys[0] = self.context_field
        return keys

    def get_storage_object(self, storage_keys):
        print('get_storage_object')
        pprint(storage_keys)
        storage = self.instance
        last_key_idx = len(storage_keys) - 1
        print(f"{last_key_idx=}")
        for idx, key in enumerate(storage_keys):
            print(f"{idx=} {key=}")
            value = None if idx == last_key_idx else {}           
            print(type(storage))     
            if isinstance(storage, (View, Form, ErrorList)):
                print('chama get_attr_value')
                storage = self.get_attr_value(self.instance, key, value)
            else:
                print('chama get_dict_value')
                storage = self.get_dict_value(storage, key, value)
            print(f"{storage=}")
        return storage

    def set_data_storage(self, storage_keys, value):
        print('set_data_storage')
        pprint(storage_keys)
        pprint(value)
        storage = self.get_storage_object(storage_keys[:-1])
        if isinstance(storage, (View, Form, ErrorList)):
            setattr(self.instance, storage_keys[-1], value)
        else:
            storage[storage_keys[-1]] = value

    def do(self, *steps):
        """Executa uma série de passos/callable.
        Recebe:
            *steps: parâmetros posicionais formando uma lista de passos.
        Retorna:
            True: indica sucesso da execução da lista inteira
            False: indica ocorrência de erro em algum passo
        Cada passo pode apresentar até 3 informações:
            - callable: referência a um método ou função 
            - storage_location: Local de armazenamento do retorno do callable.
              O local de armazenamento padrão é o self.context.
            - error_field: Nome da chave do context que guarda lista de
              mensagens de erro recebidas pelo método do_steps. Nome padrão é
              definido no init da CustomView.
        Essas iformações podem aparecer das seguintes formas:
            callable
            (storage_location, callable)
            (storage_location, callable, error_field)
            (                callable, error_field)
        storage_location e error_field podem conter pontos ".", Se for o caso,
        as partes que os pontos separam indicam uma estrutura de chaves de
        dicionários aninhados.
        Exceções tratadas para cada passo:
            StopStepsException: a execução dos passos é interompida.
            StepErrorException: a execução dos passos continua.
        Mensagens das exceções são armazenadas no error_field.
        Na ausência de exceção, o retorno do método é atribuido ao local
        indicado, seguindo as seguintes regras:
        Caso o local indicado seja:
            - um dicionário (como o padrão, self.context): Só armazena o
              retorno se este for dicionário, fazendo um update no local.
            - uma lista ou um set: Adiciona à este o retorno. Se o retorno for
              uma tupla, cada item da tupla é incluído indiviualmente.
            - outro tipo: Substitui pelo retorno
            - não exista: É criado com o valor do retorno
        """
        ok = True
        for step in steps:
            print('step', step)
            storage_location, execute, error_field = (
                self.get_step_definition(step))
            print('storage_location', storage_location)
            print('execute', execute)
            print('error_field', error_field)
            storage_keys = self.location_keys(storage_location)
            pprint(storage_keys)
            try:
                result = execute()
                print('result')
                pprint(result)
                if result is not None:
                    print('result is not None')
                    storage = self.get_storage_object(storage_keys)
                    print('storage')
                    pprint(storage)
                    if isinstance(storage, dict):
                        if isinstance(result, dict):
                            storage.update(result)
                        else:
                            raise Exception(
                                "storage_location é dict e result de callable "
                                "não é dict. Não é possível fazer "
                                "'dict.update'")
                    elif isinstance(storage, list):
                        if isinstance(result, tuple):
                            for item in result:
                                storage.append(item)
                        else:
                            storage.append(result)
                    elif isinstance(storage, set):
                        if isinstance(result, tuple):
                            for item in result:
                                storage.add(item)
                        else:
                            storage.add(result)
                    else:
                        self.set_data_storage(storage_keys, result)
            except StopStepsException as e:
                self.add_error_field_msg(error_field, e, force_init=True)
                return False
            except StepErrorException as e:
                self.add_error_field_msg(error_field, e)
                ok = False
        return ok
