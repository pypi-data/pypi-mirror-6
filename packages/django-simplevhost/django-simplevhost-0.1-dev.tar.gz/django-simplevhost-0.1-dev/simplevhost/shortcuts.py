from django.template.response import TemplateResponse

def render(request, template_name, context_data):
    if hasattr(request, 'site') and request.site:
        site_template_name = "{0}/{1}".format(
            request.site.slug,
            template_name
        )
    else:
        site_template_name = template_name
    return TemplateResponse(request, site_template_name, context_data)
