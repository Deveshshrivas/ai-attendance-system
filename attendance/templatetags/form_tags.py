from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    return field

@register.filter(name='add_id_prefix')
def add_id_prefix(field, prefix):
    if hasattr(field, 'widget'):
        field.widget.attrs.update({'id': f"{prefix}{field.auto_id}"})
    return field