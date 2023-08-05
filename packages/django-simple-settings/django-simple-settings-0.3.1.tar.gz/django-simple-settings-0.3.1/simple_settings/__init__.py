from .models import Settings

VERSION = '0.3.1'


class LazySettings(object):
    """Provides lazy settings"""
    _interface = {
        'get': 'get_item',
        'set': 'set_item',
        'delete': 'del_item',
        'all': 'to_dict'
    }

    def __getattr__(self, item):
        if item in self._interface:
            return getattr(Settings.objects, self._interface[item])
        else:
            raise AttributeError

    def __getitem__(self, item):
        return Settings.objects.to_dict()[item]

settings = LazySettings()
