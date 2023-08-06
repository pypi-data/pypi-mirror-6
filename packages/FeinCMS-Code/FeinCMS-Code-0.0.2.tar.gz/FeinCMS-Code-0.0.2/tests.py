from __future__ import absolute_import, unicode_literals
import datetime
from django.conf import settings

settings.configure(
    DATABASES={'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }},
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'feincms',
    ),
)

from django.test import TestCase
from django.core.management import call_command
from feincms.module.page.models import Page
from feincms_code.content import CodeContent

Page.register_templates(
    {'title': 'Page',
     'path': 'page/page.html',
     'regions': (
         ('main', 'Main content area'),
     )},
)
Page.create_content_type(CodeContent)


call_command('syncdb', interactive=False)


class CodeCase(TestCase):
    def test_python(self):
        cc = CodeContent(code="import test", language="python")
        self.assertEqual(
            cc.html(),
            """<div class="highlight"><pre><span class="kn">import</span> """
            + """<span class="nn">test</span>\n</pre></div>\n"""
        )
