import six

from django import forms
from django.db import models
from django import forms
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .registry import registry as default_registry
from .widgets import ChoiceWidget, MultipleChoiceWidget, TextWidget


class FieldBase(object):
    def __init__(self, autocomplete=None, registry=None, widget=None,
            widget_js_attributes=None, autocomplete_js_attributes=None,
            extra_context=None, *args, **kwargs):

        if widget:
            # BC: maybe defining the autocomplete as a widget argument ?
            autocomplete = getattr(widget, 'autocomplete', None)
            if autocomplete:
                self.autocomplete = autocomplete

        if not getattr(self, 'autocomplete', False):
            # new DRY style support
            registry = registry or default_registry
            self.autocomplete = registry.get_autocomplete_from_arg(
                autocomplete)

        widget = widget or self.widget
        if isinstance(widget, type):
            self.widget = widget(autocomplete, widget_js_attributes,
                    autocomplete_js_attributes, extra_context)

        parents = super(FieldBase, self).__self_class__.__bases__
        if (forms.ModelChoiceField in parents or
                forms.ModelMultipleChoiceField in parents):
            kwargs['queryset'] = self.autocomplete.choices

        super(FieldBase, self).__init__(*args, **kwargs)

    def validate(self, value):
        """
        Wrap around Autocomplete.validate_values().
        """
        super(FieldBase, self).validate(value)

        # FIXME: we might actually want to change the Autocomplete API to
        # support python values instead of raw values, that would probably be
        # more performant.
        values = self.prepare_value(value)

        if value and not self.autocomplete(values=values).validate_values():
            raise forms.ValidationError('%s cannot validate %s' % (
                self.autocomplete.__name__, value))


class ModelChoiceField(FieldBase, forms.ModelChoiceField):
    widget = ChoiceWidget


class ModelMultipleChoiceField(FieldBase,
        forms.ModelMultipleChoiceField):
    widget = MultipleChoiceWidget


class GenericModelChoiceField(FieldBase, forms.Field):
    """
    Simple form field that converts strings to models.
    """
    widget = ChoiceWidget

    def prepare_value(self, value):
        """
        Given a model instance as value, with content type id of 3 and pk of 5,
        return such a string '3-5'.
        """
        if isinstance(value, six.string_types):
            # Apparently there's a bug in django, that causes a python value to
            # be passed here. This ONLY happens when in an inline ....
            return value
        elif isinstance(value, models.Model):
            return '%s-%s' % (ContentType.objects.get_for_model(value).pk,
                              value.pk)

    def to_python(self, value):
        """
        Given a string like '3-5', return the model of content type id 3 and pk
        5.
        """
        if not value:
            return value

        content_type_id, object_id = value.split('-', 1)
        try:
            content_type = ContentType.objects.get_for_id(content_type_id)
        except ContentType.DoesNotExist:
            raise forms.ValidationError(u'Wrong content type')
        else:
            model = content_type.model_class()

        return model.objects.get(pk=object_id)


class GenericModelMultipleChoiceField(GenericModelChoiceField):
    """
    Simple form field that converts strings to models.
    """
    widget = MultipleChoiceWidget

    def prepare_value(self, value):
        return [super(GenericModelMultipleChoiceField, self
            ).prepare_value(v) for v in value]

    def to_python(self, value):
        return [super(GenericModelMultipleChoiceField, self).to_python(v)
            for v in value]
