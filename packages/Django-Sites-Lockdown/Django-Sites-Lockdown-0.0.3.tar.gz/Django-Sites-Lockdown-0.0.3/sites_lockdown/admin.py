from django.contrib.sites.admin import SiteAdmin

SiteAdmin.actions = None
SiteAdmin.has_delete_permission = lambda self, request, obj=None: False
SiteAdmin.has_add_permission = lambda self, request, obj=None: False
SiteAdmin.search_fields = tuple()
