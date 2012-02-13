from django.db import models
from django.db.models import Q

# Create your models here.

HTTP_SCHEMES = (
    ('http', 'http'),
    ('https', 'https'),
)


class Site(models.Model):
    hostname = models.CharField(max_length=70)
    path = models.CharField(max_length=255)
    scheme = models.CharField(max_length=5, choices=HTTP_SCHEMES)
    ignore = models.BooleanField(default=False)
    update_on = models.DateTimeField(auto_now=True)
    inserted_on = models.DateTimeField(auto_now_add=True)

    def _url(self):
        return '%s://%s%s' % (self.scheme, self.hostname, self.path)
    url = property(_url)

    def _working_credentials(self):
        return self.credential_set.filter(Q(works=True)|Q(keeper=True))
    credentials = property(_working_credentials)

    def __unicode__(self):
        return self.url
        
    class Meta:
        ordering = ['hostname', 'path']

class Credential(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    works = models.BooleanField(default=False)
    update_on = models.DateTimeField(auto_now=True)
    inserted_on = models.DateTimeField(auto_now_add=True)
    site = models.ForeignKey(Site)
    last_http_code = models.IntegerField(default=0)
    last_title = models.CharField(max_length=200,default='',blank=True)
    last_lag = models.IntegerField(default=999999)
    keeper = models.BooleanField(default=False)

    def _url(self):
        return self.site.url
    url = property(_url)
    
    def __unicode__(self):
        return "%s://%s:%s@%s%s" %(self.site.scheme, self.username, self.password, self.site.hostname, self.site.path)
        
    class Meta:
        ordering = ["-works", "last_http_code", "last_title",]
        unique_together = (("username", "password", "site"),)
        
class Proxy(models.Model):
    hostname = models.CharField(db_index=True, unique=True, max_length=70)
    works = models.BooleanField(default=True)
    lag = models.IntegerField(default=999999)
    update_on = models.DateTimeField(auto_now=True)
    inserted_on = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return "%s (%s, %s ms)" %(self.hostname, self.works, self.lag)
    class Meta:
        ordering = ['-works', 'lag']
        verbose_name_plural = "proxies"
        
from django.contrib import admin
admin.site.register(Site)
admin.site.register(Credential)
admin.site.register(Proxy)

