from django.db import models

class Aluno(models.Model):
    ra = models.CharField(max_length=20)
    nome = models.CharField(max_length=200)
    codigo_turma = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nome} - {self.ra}"
