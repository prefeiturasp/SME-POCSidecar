from django.db import models


class DRE(models.Model):
    nome = models.CharField(max_length=200)


class Escola(models.Model):
    nome = models.CharField(max_length=200)
    dre = models.ForeignKey(DRE, on_delete=models.CASCADE, related_name="escolas")


class Turma(models.Model):
    codigo = models.CharField(max_length=20)
    serie = models.CharField(max_length=20)
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name="turmas")
