from . import Settings


def simple_settings(request):
    """Returns a lazy 'simple_settings' context variable."""
    return {
        'simple_settings': lambda: Settings.objects.to_dict(),
    }
