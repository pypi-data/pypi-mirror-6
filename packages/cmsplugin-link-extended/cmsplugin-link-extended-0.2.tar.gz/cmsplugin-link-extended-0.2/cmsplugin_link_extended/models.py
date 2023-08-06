"""Models for the ``cmsplugin_link_extended`` app."""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangocms_link.models import Link


class LinkExtended(Link):
    """This model extends the original Link model."""

    css_classes = models.CharField(
        max_length=256,
        verbose_name=_('CSS Classes'),
        blank=True,
    )
