from django.template.response import TemplateResponse


def get_template_name(request, template_name):
    if hasattr(request, 'site') and request.site:
        site_template_name = "{0}/{1}".format(
            request.site.slug,
            template_name
        )
    else:
        site_template_name = template_name

    return site_template_name


def render(request, template_name, context_data):
    site_template_name = get_template_name(request, template_name)
    return TemplateResponse(request, site_template_name, context_data)
