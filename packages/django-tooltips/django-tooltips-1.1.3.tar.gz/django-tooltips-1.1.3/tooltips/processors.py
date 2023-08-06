from .models import Tooltip

def tooltips(request):
    tooltips = Tooltip.objects.filter(url=request.path)

    return {
        'tooltips': tooltips
    }