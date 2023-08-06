from django.db import models

class Site(models.Model):
    domain = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    slug = models.SlugField()
    tracking_code = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.title

class SiteModelMixin:
    @classmethod
    def for_site(cls, site):
        return cls.objects.filter(site=site)
