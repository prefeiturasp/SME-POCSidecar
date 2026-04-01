from rest_framework import serializers
from .models import DRE, Escola, Turma


class TurmaSerializer(serializers.ModelSerializer):
    serie = serializers.SerializerMethodField()
    turma = serializers.SerializerMethodField()

    class Meta:
        model = Turma
        fields = ['id', 'codigo', 'escola', 'serie', 'turma']

    def get_serie(self, obj):
        text = obj.serie or ""
        return text[:-1] if len(text) >= 2 else text

    def get_turma(self, obj):
        text = obj.serie or ""
        return text[-1] if len(text) >= 2 else ""


class EscolaSerializer(serializers.ModelSerializer):
    turmas = TurmaSerializer(many=True, read_only=True)

    class Meta:
        model = Escola
        fields = "__all__"


class DRESerializer(serializers.ModelSerializer):
    escolas = EscolaSerializer(many=True, read_only=True)

    class Meta:
        model = DRE
        fields = "__all__"
