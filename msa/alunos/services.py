from .models import Aluno

class AlunoService:
    @staticmethod
    def get_all_alunos():
        return Aluno.objects.all()
