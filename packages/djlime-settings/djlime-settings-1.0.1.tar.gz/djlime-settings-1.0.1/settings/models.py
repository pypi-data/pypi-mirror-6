from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Setting(models.Model):
    key = models.CharField(_('key'), max_length=255, unique=True)
    value = models.TextField(_('value'))

    class Meta:
        ordering = ('id',)
        db_table = 'settings'
        verbose_name = _('setting')
        verbose_name_plural = _('settings')

    def __str__(self):
        return self.key