from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class SettingsManager(models.Manager):
    _cached_settings = {}

    def to_dict(self):
        """Returns a dict like key => value"""
        if not self._cached_settings:
            for s in self.all():
                if s.value_type == 'bool':
                    self._cached_settings[s.key] = True if s.value.lower() == "true" else False
                else:
                    self._cached_settings[s.key] = globals()['__builtins__'][s.value_type](s.value)
        return self._cached_settings

    def set_item(self, key, value):
        """Sets setting ``key`` to ``value```"""
        value_type = type(value).__name__
        if value_type not in ('bool', 'float', 'int', 'str'):
            raise ValueError('Unsupported value type.')

        obj, created = self.get_or_create(key=key, defaults={'value': value, 'value_type': value_type})
        if not created:
            obj.key = key
            obj.value = value
            obj.value_type = value_type
            obj.save()
        return obj

    def del_item(self, key):
        """Deletes setting ``key``"""
        try:
            self.get(key=key).delete()
        except self.model.DoesNotExist:
            raise KeyError(key)

    def clear_cache(self):
        """Clear cache of settings"""
        self._cached_settings = {}


class Settings(models.Model):
    """Provides settings model"""
    VALUE_TYPE_CHOICES = (
        ('bool', _('Boolean')),
        ('float', _('Float')),
        ('int', _('Integer')),
        ('str', _('String')),
    )
    key = models.CharField(_('Key'), max_length=255, unique=True)
    value = models.CharField(_('Value'), max_length=255, default='', blank=True)
    value_type = models.CharField(_('Type'), max_length=10, choices=VALUE_TYPE_CHOICES,
                                  default=VALUE_TYPE_CHOICES[3][0], blank=True)

    objects = SettingsManager()

    class Meta:
        verbose_name = _('setting')
        verbose_name_plural = _('settings')

    def __unicode__(self):
        return "%s: %s" % (self.key, self.value)

    def clean(self):
        if self.value_type == 'bool' and self.value not in ("true", "false"):
            raise ValidationError({'value': [_('For boolean type available case-insensitive values: true, false')]})
        elif self.value_type == 'float':
            try:
                float(self.value)
            except ValueError:
                raise ValidationError({'value': [_('Incorrect float value')]})
        elif self.value_type == 'int':
            try:
                int(self.value)
            except ValueError:
                raise ValidationError({'value': [_('Incorrect integer value')]})


@receiver(signal=(post_save, post_delete), sender=Settings)
def settings_update_handler(**kwargs):
    """Clear settings cache"""
    instance = kwargs.pop('instance')
    instance._default_manager.clear_cache()
