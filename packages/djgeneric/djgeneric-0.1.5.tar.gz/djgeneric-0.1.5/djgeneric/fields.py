
from django import forms


class UpperCharField(forms.CharField):

    def clean(self, value):
        value = super(UpperCharField, self).clean(value)
        return value.upper()

    def widget_attrs(self, widget):
        attrs = super(UpperCharField, self).widget_attrs(widget)
        if 'class' in attrs:
            attrs['class'] += ' uppercase'
        else:
            attrs['class'] = 'uppercase'
        return attrs
