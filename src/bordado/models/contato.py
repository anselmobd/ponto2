from pprint import pprint

from django.db import models

from bordado.models.cliente import Cliente


__all__ = [
    'Contato',
]


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
