__all__ = [
    'StopStepsException',
    'StepErrorException',
]


class StopStepsException(Exception):
    '''
    Use StopStepsException, passando mensagem, para interromper o loop que 
    processa todos os passos no méthodo do_steps da classe CustomView.
    O método retornará False e colocará a mensagem, como único elemento da
    lista que está na chave msg_error (nome customizável) do dict context.
    '''
    def __init__(self, message=""):
        self.message = message
        super().__init__(f"Processo interrompido: {self.message}")


class StepErrorException(Exception):
    '''
    Use StepErrorException, passando mensagem, para o méthodo do_steps da
    classe CustomView acumular a mensagem na lista que está na chave msg_error
    (nome customizável) do dict context. O método retornará False ao final
    de todos os passos.
    '''
    ...
