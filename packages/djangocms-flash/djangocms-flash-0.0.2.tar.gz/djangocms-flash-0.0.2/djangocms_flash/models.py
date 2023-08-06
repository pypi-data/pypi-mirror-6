import os
import re

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from cms.utils.compat.dj import python_2_unicode_compatible


@python_2_unicode_compatible
class Flash(CMSPlugin):
    file = models.FileField(
        _('file'), upload_to=CMSPlugin.get_media_path,
        help_text=_('use swf file'))

    width = models.CharField(_('width'), max_length=6)
    height = models.CharField(_('height'), max_length=6)

    def __str__(self):
        return u"%s" % os.path.basename(self.file.path)
    
    def get_height(self):
        return fix_unit(self.height)
    
    def get_width(self):
        return fix_unit(self.width)


def fix_unit(value):
    if not re.match(r'.*[0-9]$', value):
        # no unit, add px
        return value + "px"
    return value 
