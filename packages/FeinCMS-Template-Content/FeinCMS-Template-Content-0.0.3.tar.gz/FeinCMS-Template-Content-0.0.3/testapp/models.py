from feincms_template_content.models import TemplateContent
from feincms.module.page.models import Page

Page.register_templates({
    'title': 'Standard template',
    'path': 'feincms/page.html',
    'regions': (
        ('main', 'Main content area'),
    ),
})


class TestContent(TemplateContent):
    class Meta(object):
        abstract = True


class CustomContent(TemplateContent):
    class Meta(object):
        abstract = True

    template_choices = (
        ("content/custom/1.html", "t1"),
        ("content/custom/2.html", "t2"),
    )

CreatedTestContent = Page.create_content_type(TestContent)
CreatedCustomContent = Page.create_content_type(CustomContent)
