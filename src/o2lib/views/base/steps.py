from pprint import pprint

from django.apps import apps
from django.shortcuts import redirect, render
from django.views import View

from o2lib.views.base.exception import (
    StepErrorException,
    StopStepsException, 
)

__all__ = ['Steps']


class Steps():
    """
    Base para método "do steps"

    """

    def __init__(self, context=[], error_field='msg_error'):
        """
        Inicializa parâmetros:
        context
            dict de dados
        error_field
            Nome da chave do context que guarda lista de mensagens de erro recebidas pelo método do_steps.
        """
        self.error_field = error_field
        self.steps_context = context

    def add_error_field_msg(self, error_field, message, force_init=False):
        if force_init or error_field not in self.steps_context:
            self.steps_context.update({
                error_field: [],
            })
        self.steps_context[error_field].append(message)

    def get_step_definition(self, step):
        return_storage = ''
        error_field = self.error_field
        if isinstance(step, tuple):
            if isinstance(step[0], str):
                return_storage = step[0]
                next_values = step[1:]
            execute = next_values[0]
            if len(next_values) > 1:
                error_field = next_values[1]
        else:
            execute = step
        return return_storage, execute, error_field

    def get_data_storage(self, return_storage):
        keys = return_storage.split('.')
        if keys[0] == '':
            keys[0] = 'context'
        storage = getattr(self, keys[0], None)
        for key in keys[1:]:
            storage = storage[key]
        return storage

    def set_data_storage(self, return_storage, value):
        keys = return_storage.split('.')
        if keys[0] == '':
            keys[0] = 'context'
        if len(keys) == 1:
            setattr(self, keys[0], value)
        else:
            storage = getattr(self, keys[0], None)
            for key in keys[1:-1]:
                if key not in storage:
                    storage[key] = dict()
                storage = storage[key]
            if isinstance(storage, dict):
                storage[keys[-1]] = value

    def do(self, *steps):
        """Executa uma série de passos/callable.
        
        Recebe:
            *steps: parâmetros posicionais formando uma lista de passos.
        
        Retorna:
            True: indica sucesso da execução da lista inteira
            False: indica ocorrência de erro em algum passo
        
        Cada passo pode apresentar até 3 informações:
            - callable: referência a um método ou função 
            - return_storage: Local de armazenamento do retorno do callable.
              O local de armazenamento padrão é o self.context.
            - error_field: Nome da chave do context que guarda lista de
              mensagens de erro recebidas pelo método do_steps. Nome padrão é definido no init da CustomView.
        Essas iformações podem aparecer das seguintes formas:
            callable
            (return_storage, callable)
            (return_storage, callable, error_field)
            (                callable, error_field)

        return_storage e error_field podem conter pontos ".", Se for o caso, as partes que os pontos separam indicam uma estrutura de chaves de dicionários aninhados.

        Exceções tratadas para cada passo:
            StopStepsException: a execução dos passos é interompida.
            StepErrorException: a execução dos passos continua.
        Mensagens das exceções são armazenadas no error_field.

        Na ausência de exceção, o retorno do método é atribuido ao local indicado, seguindo as seguintes regras:
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
            return_storage, execute, error_field = (
                self.get_step_definition(step))
            try:
                result = execute()
                if result is not None:
                    storage = self.get_data_storage(return_storage)
                    if isinstance(storage, dict):
                        if isinstance(result, dict):
                            storage.update(result)
                        else:
                            raise Exception(
                                "return_storage é dict e result de callable"
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
                        self.set_data_storage(return_storage, result)
            except StopStepsException as e:
                self.add_error_field_msg(error_field, e, force_init=True)
                return False
            except StepErrorException as e:
                self.add_error_field_msg(error_field, e)
                ok = False
        return ok
