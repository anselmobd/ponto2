import datetime

from django.test import TestCase

from bordado.models import Cliente


class ClienteTestCase(TestCase):
    fixtures = ["test_auth.json", "test_bordado.json"]

    def test_cadastro(self):
        """Cliente cadastrado"""
        cliente = Cliente.objects.get(apelido="Primeiro")
        # self.assertEqual(cliente.apelido, "Primeiro")
        self.assertEqual(cliente.nome, "Primeiro Confecções")
        self.assertEqual(cliente.cnpj9, 1)
        self.assertEqual(cliente.cnpj4, 1)
        self.assertEqual(cliente.cnpj2, 0)
        self.assertEqual(cliente.conta_corrente, False)
        self.assertEqual(cliente.parcelamento, "10")
        self.assertEqual(cliente.cnpj, "00000001/0001-00!")
        self.assertEqual(cliente.usuario.username, "admin")
        self.assertEqual(
            cliente.quando,
            datetime.datetime(
                2023, 6, 14, 3, 20, 57, 991000,
                tzinfo=datetime.timezone.utc
            )
        )
