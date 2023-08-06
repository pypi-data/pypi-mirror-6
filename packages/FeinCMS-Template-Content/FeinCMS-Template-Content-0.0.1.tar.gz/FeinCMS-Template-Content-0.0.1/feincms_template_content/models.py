import re
from django.db import models
from django.template import Context, RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

snake_case_regex = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


class TemplateContent(models.Model):
    class Meta(object):
        abstract = True

    template_choices = None

    context_object_name = "content"
    template_folder_name = None

    @classmethod
    def initialize_type(class_, **kwargs):
        # Add a field to represent the chosen template.
        # This must be in initialize_type to allow subclasses
        # to customize the template_choices

        class_._ensure_template_choices(**kwargs)

        default = class_.template_choices[0][0]
        class_.add_to_class(
            'template',
            models.CharField(
                _('template'),
                max_length=255,
                choices=class_.template_choices,
                default=default,
            )
        )

    @classmethod
    def _ensure_template_choices(class_, **kwargs):
        if not class_.template_choices:
            name = class_._generate_template_name(**kwargs)
            class_.template_choices = (
                ('content/%s.html' % name, 'Normal'),
            )

    @classmethod
    def _generate_template_name(class_, **kwargs):
        # convert class name from CamelCasse to snake_case
        class_name = class_.__name__
        name = snake_case_regex.sub(r'_\1', class_name)
        name = name.lower()
        # remove trailing _content if present
        name = name.rsplit("_content", 1)[0]
        return name

    def get_template_names(self, **kwargs):
        for template, name in self.template_choices:
            if self.template == template:
                return [template]

        return [self.template_choices[0][0]]

    def get_context_object_name(self, **kwargs):
        return self.context_object_name

    def get_context_data(self, **kwargs):
        return {self.get_context_object_name(**kwargs): self}

    def get_context(self, **kwargs):
        if 'request' in kwargs.keys():
            return RequestContext(
                kwargs['request'],
                dict_=self.get_context_data(**kwargs),
            )
        else:
            return Context(dict_=self.get_context_data(**kwargs))

    def render(self, **kwargs):
        return render_to_string(
            template_name=self.get_template_names(**kwargs),
            context_instance=self.get_context(**kwargs),
        )
