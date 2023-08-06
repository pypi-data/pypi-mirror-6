from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from feincms_template_content.models import TemplateContent

from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers, guess_lexer
from pygments.formatters import HtmlFormatter

LANGUAGE_CHOICES = list(
    (l[1][0], l[0]) for l in get_all_lexers()
)
LANGUAGE_CHOICES.sort(key=lambda l: l[0])
LANGUAGE_CHOICES = tuple(LANGUAGE_CHOICES)

@python_2_unicode_compatible
class CodeContent(TemplateContent):
    class Meta(object):
        abstract = True
        verbose_name = 'code'
        verbose_name_plural = 'codes'

    language = models.CharField(
        _("language"),
        max_length=255,
        choices = LANGUAGE_CHOICES,
    )
    code = models.TextField(_("code"), blank=True)

    _html = None

    def html(self):
        if self._html is None:
            self._html = highlight(
                self.code,
                self.get_lexer(),
                self.get_formatter(),
            )

        return self._html

    def get_lexer(self):
        return get_lexer_by_name(self.language)

    def get_formatter(self):
        return HtmlFormatter()

    def __str__(self):
        return u"code"
