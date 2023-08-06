from .models import Tooltip

def tooltips(request):
    tooltips = Tooltip.objects.filter(url=request.path)
    print request.path, tooltips

    return {
        'tooltips': tooltips
    }