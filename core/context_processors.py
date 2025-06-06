from .models import Service, Master

def common_context(request):
    """
    Контекстный процессор для добавления общих данных во все шаблоны.
    """
    context = {
        'masters': Master.objects.filter(is_active=True),
        'services': Service.objects.all(),
        
    }
    return context