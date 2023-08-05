from .models import Settings

VERSION = '0.1'


class LazySettings(object):



    def __getattr__(self, item):
        return getattr(Settings.objects.to_dict(), item)

    def __getitem__(self, item):
        return Settings.objects.to_dict()[item]

settings = LazySettings()
