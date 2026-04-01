from .models import DRE

class EstruturaService:
    @staticmethod
    def get_all_dres():
        return DRE.objects.all()
