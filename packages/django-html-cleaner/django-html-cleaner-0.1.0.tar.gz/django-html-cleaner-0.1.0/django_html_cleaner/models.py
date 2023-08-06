from django.conf import settings
from django.db import models
from django.utils.encoding import smart_text
from .cleaner import Cleaner


class SanitizedCharField(models.CharField):
    """
    Use anywhere you would use a ``CharField``. Sanitizes HTML.

    ``cleaner``:
        An instance of ``django_html_cleaner.cleaner.Cleaner()``.
        Provide your own instance if you want to do more than
        just remove JavaScript and unknown/special HTML tags.
    """

    def __init__(self, cleaner=None, *args, **kwargs):
        self.cleaner = cleaner or Cleaner()
        super(SanitizedCharField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(SanitizedCharField, self).to_python(value)
        value = self.cleaner.clean(value)
        return smart_text(value)


class SanitizedTextField(models.TextField):
    """
    Use anywhere you would use a ``TextField``. Sanitizes HTML.

    ``cleaner``:
        An instance of ``django_html_cleaner.cleaner.Cleaner()``.
        Provide your own instance if you want to do more than
        just remove JavaScript and unknown/special HTML tags.
    """

    def __init__(self, cleaner=None, *args, **kwargs):
        self.cleaner = cleaner or Cleaner()
        super(SanitizedTextField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(SanitizedTextField, self).to_python(value)
        value = self.cleaner.clean(value)
        return smart_text(value)

    def get_prep_value(self, value):
        value = super(SanitizedTextField, self).get_prep_value(value)
        value = self.cleaner.clean(value)
        return value


if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^sanitizer\.models\.SanitizedCharField"])
    add_introspection_rules([], ["^sanitizer\.models\.SanitizedTextField"])
