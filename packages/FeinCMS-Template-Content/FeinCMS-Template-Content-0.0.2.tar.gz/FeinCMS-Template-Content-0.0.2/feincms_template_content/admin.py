from feincms.admin.item_editor import FeinCMSInline


class BaseTemplateContentAdmin(FeinCMSInline):
    def __init__(self, *args, **kwargs):
        self.exclude = list(self.exclude or [])
        if len(self.model.template_choices) <= 1:
            self.exclude.append('template')

        super(BaseTemplateContentAdmin,
              self).__init__(*args, **kwargs)
