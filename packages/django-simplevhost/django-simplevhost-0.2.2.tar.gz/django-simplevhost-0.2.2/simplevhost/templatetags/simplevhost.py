from django import template

register = template.Library()


@register.filter(name='for_site')
def for_site(value, site):
    return [x for x in value if x.site == site]

