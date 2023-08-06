from django.conf import settings
from django.utils.cache import patch_vary_headers
from simplevhost.models import Site

SIMPLEVHOST_URLCONF = getattr(settings, 'SIMPLEVHOST_MIDDLEWARE_URLCONF_MAP',
    {})
SITES = {}


class SimpleVHostMiddleware(object):
    """ provides a simple, lightweight infrastructure for using the same
    backend
    with multiple frontends from the same django instance
    """

    def process_request(self, request):
        global SITES

        if len(SITES) == 0:
            SITES = {site.domain: site for site in Site.objects.all()}

        host = request.get_host()
        if ':' in host:
            host, _ = host.split(":", 1)
        try:
            possible_sites = [
                site
                for domain, site
                in SITES.items()
                if domain in host
            ]
            if len(possible_sites) > 0:
                request.site = possible_sites[0]
                request.urlconf = SIMPLEVHOST_URLCONF[request.site.slug]
            else:
                request.site = None
        except KeyError:
            return


    def process_template_response(self, request, response):

        if not hasattr(request, "site") or request.site is None:
            return response

        response.context_data[
            'site'] = "" if request.site is None else request.site.slug
        return response

    def process_response(self, request, response):
        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))

        return response
