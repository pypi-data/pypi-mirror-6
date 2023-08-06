from django.utils.translation import ugettext_lazy as _
from feincms.content.richtext.models import (
    RichTextContent as BaseRichTextContent)
from feincms_template_content.models import TemplateContent


class RichTextContent(TemplateContent, BaseRichTextContent):
    class Meta:
        abstract = True
        verbose_name = _('rich text')
        verbose_name_plural = _('rich texts')
