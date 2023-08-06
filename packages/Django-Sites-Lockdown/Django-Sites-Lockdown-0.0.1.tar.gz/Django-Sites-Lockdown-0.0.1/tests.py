from django.conf import settings

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=(
        'django.contrib.admin',
        'django.contrib.sites',
        'sites_lockdown',
    )
)


from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib import admin
from django.contrib.sites.models import Site

admin.autodiscover()
site_admin = admin.site._registry[Site]
factory = RequestFactory()


class SiteAdminTestCase(TestCase):
    def test_no_add(self):
        request = factory.get('/admin/fake')
        self.assertEqual(
            site_admin.has_add_permission(request),
            False,
        )

    def test_no_delete(self):
        request = factory.post('/admin/fake')
        self.assertEqual(
            site_admin.has_delete_permission(request),
            False,
        )

    def test_no_delete_obj(self):
        request = factory.post('/admin/fake')
        site = Site(pk=33, name='example.com', domain='example.com')
        self.assertEqual(
            site_admin.has_delete_permission(request, site),
            False,
        )
