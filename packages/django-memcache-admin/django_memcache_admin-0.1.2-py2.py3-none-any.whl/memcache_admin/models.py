
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Dashboard(models.Model):
    class Meta:
        verbose_name = _('Memcache Dashboard')
        verbose_name_plural = _('Memcache Dashboard')
        managed = False