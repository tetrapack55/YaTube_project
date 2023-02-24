from datetime import datetime

current_year: int = datetime.now().year


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': current_year
    }
