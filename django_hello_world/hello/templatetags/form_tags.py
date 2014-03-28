from django import template
register = template.Library()


@register.inclusion_tag('hello/tags/render_field.html')
def render_field(field):
    return {
        "field": field,
    }


@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})
