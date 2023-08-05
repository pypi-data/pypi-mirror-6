from .models import Settings

VERSION = '0.2'


class LazySettings(object):
    """Provides lazy settings"""
    def __getattr__(self, item):
        if item == 'set':
            return Settings.objects.set_item
        elif item == 'delete':
            return Settings.objects.del_item
        else:
            return getattr(Settings.objects.to_dict(), item)

    def __getitem__(self, item):
        return Settings.objects.to_dict()[item]

settings = LazySettings()
