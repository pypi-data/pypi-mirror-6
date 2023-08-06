from django.conf import settings
from django.db import models
from .cleaner import Cleaner


def default_cleaner():
    allowed_tags = getattr(settings, 'HTML_CLEANER_ALLOWED_TAGS', None)
    allowed_attributes = getattr(settings,
                                 'HTML_CLEANER_ALLOWED_ATTRIBUTES',
                                 None)
    allowed_styles = getattr(settings, 'HTML_CLEANER_ALLOWED_STYLES', None)
    create_parent = getattr(settings, 'HTML_CLEANER_PARENT_TAG', None)

    return Cleaner(allowed_tags=allowed_tags,
                   allowed_attributes=allowed_attributes,
                   allowed_styles=allowed_styles,
                   create_parent=create_parent)


class SanitizedCharField(models.CharField):
    """
    Use anywhere you would use a ``CharField``. Sanitizes HTML.

    ``cleaner``:
        An instance of ``django_html_cleaner.cleaner.Cleaner()``.
        Provide your own instance if you want to do more than
        just remove JavaScript and unknown/special HTML tags.
    """

    def __init__(self, cleaner=None, *args, **kwargs):
        self.cleaner = cleaner or default_cleaner()
        super(SanitizedCharField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = super(SanitizedCharField, self).pre_save(model_instance, add)
        if value and value.strip():
            clean_value = self.cleaner.clean(value)
            if value != clean_value:
                setattr(model_instance, self.attname, clean_value)
            value = clean_value
        return value


class SanitizedTextField(models.TextField):
    """
    Use anywhere you would use a ``TextField``. Sanitizes HTML.

    ``cleaner``:
        An instance of ``django_html_cleaner.cleaner.Cleaner()``.
        Provide your own instance if you want to do more than
        just remove JavaScript and unknown/special HTML tags.
    """

    def __init__(self, cleaner=None, *args, **kwargs):
        self.cleaner = cleaner or default_cleaner()
        super(SanitizedTextField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = super(SanitizedTextField, self).pre_save(model_instance, add)
        if value and value.strip():
            clean_value = self.cleaner.clean(value)
            if value != clean_value:
                setattr(model_instance, self.attname, clean_value)
            value = clean_value
        return value


if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^django_html_cleaner\.models\.SanitizedCharField"])
    add_introspection_rules([], ["^django_html_cleaner\.models\.SanitizedTextField"])
