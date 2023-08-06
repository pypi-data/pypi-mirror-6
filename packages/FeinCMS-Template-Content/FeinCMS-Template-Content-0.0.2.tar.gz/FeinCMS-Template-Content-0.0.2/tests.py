from django.conf import settings

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=(
        'feincms',
        'feincms.module.page',
        'testapp',
    )
)


from django.test import TestCase
from django.template.context import Context
from django.template import RequestContext
from feincms_template_content.models import TemplateContent
from testapp.models import (
    CreatedTestContent,
    CreatedCustomContent,
)
from mock import Mock
from django.contrib import admin
from feincms.module.page.models import Page


admin.autodiscover()

#TODO:
# test that **kwargs get passed around the methods properly


class TemplateContentTestCase(TestCase):
    def test_folder_name(self):
        tests = (
            ('class', 'class'),
            ('Class', 'class'),
            ('CLASS', 'class'),
            ('ClassName', 'class_name'),
            ('className', 'class_name'),
            ('CLASSName', 'class_name'),
            ('ClassNAME', 'class_name'),
            ('classNAME', 'class_name'),
            ('ClassNAMEExtra', 'class_name_extra'),
            ('classNAMEExtra', 'class_name_extra'),
            ('TestContent', 'test'),
            ('test_content', 'test'),
        )
        for name, check in tests:
            test_type = type(name, (TemplateContent,), {
                '__module__': TemplateContent.__module__,
                'Meta': type("Meta", (object,), {'abstract': True}),
            })
            result = test_type._generate_template_name()
            self.assertEqual(result, check)

    def test_template_field(self):
        template_field = None
        for field in CreatedTestContent._meta.fields:
            if field.name == 'template':
                template_field = field

        assert template_field is not None, 'template field not found'
        self.assertEqual(template_field.default,
                         CreatedTestContent.template_choices[0][0])

    def test_default_template_choices(self):
        self.assertEqual(TemplateContent.template_choices, None)

    def test_auto_template_choices(self):
        self.assertEqual(CreatedTestContent.template_choices,
                         (('content/test.html', 'Normal'),))

    def test_manual_template_choices(self):
        self.assertEqual(CreatedCustomContent.template_choices,
                         (('content/custom/1.html', 't1'),
                          ('content/custom/2.html', 't2')))

    def test_get_context_object_name(self):
        c = CreatedTestContent()
        self.assertEqual(c.get_context_object_name(), 'content')
        mock_name = Mock()
        c.context_object_name = mock_name
        self.assertIs(c.get_context_object_name(), mock_name)

    def test_get_context_data(self):
        c = CreatedTestContent()
        self.assertEqual(c.get_context_data(), {'content': c})
        mock_name = Mock()
        c.context_object_name = mock_name
        self.assertEqual(c.get_context_data(), {mock_name: c})

    def test_get_context(self):
        c = CreatedTestContent()
        data = Mock(spec_set=[])
        c.get_context_data = Mock(spec_set=[], return_value=data)
        ctx = c.get_context()
        self.assertEqual(type(ctx), Context)
        self.assertEqual(len(ctx.dicts), 2)
        self.assertEqual(ctx.dicts[1], data)

    def test_get_context_request(self):
        c = CreatedTestContent()
        request = Mock(spec_set=[])
        ctx = c.get_context(request=request)
        self.assertEqual(type(ctx), RequestContext)

    def test_render(self):
        c = CreatedTestContent()
        self.assertEqual(c.render().strip(), 'test')

    def test_admin_form_hidden_template_field(self):
        inline_class = CreatedTestContent.feincms_item_editor_inline
        inline = inline_class(Page, admin.site)
        self.assertIn('template', inline.exclude)

    def test_admin_form_template_field(self):
        inline_class = CreatedCustomContent.feincms_item_editor_inline
        inline = inline_class(Page, admin.site)
        self.assertNotIn('template', inline.exclude)
