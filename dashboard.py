"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'pressurenet.dashboard.PressureNETIndexDashboard'
"""
import random

from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache


from grappelli.dashboard import modules, Dashboard


class CacheModule(modules.DashboardModule):
    template = 'admin/includes/cache_module.html'

    def is_empty(self):
        return False

    def init_with_context(self, context):
        cache_key = 'cache_test:%s' % (random.random(),)
        cache_value = random.random()

        # set to cache
        cache.set(cache_key, cache_value, 60)

        # get from cache
        cache_online = cache.get(cache_key) == cache_value

        context['cache_online'] = cache_online


class PressureNETIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        # append a group for "Administration" & "Applications"
        #self.children.append(modules.Group(
        #    _('Group: Administration & Applications'),
        #    column=1,
        #    collapsible=True,
        #    children = [
        #        modules.AppList(
        #            _('Administration'),
        #            column=1,
        #            collapsible=False,
        #            models=('django.contrib.*',),
        #        ),
        #        modules.AppList(
        #            _('Applications'),
        #            column=1,
        #            css_classes=('collapse closed',),
        #            exclude=('django.contrib.*',),
        #        )
        #    ]
        #))

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('Administration'),
            column=1,
            collapsible=True,
            models=('django.contrib.*',),
        ))

        # append an app list module for "Applications"
        self.children.append(modules.ModelList(
            _('Readings'),
            collapsible=True,
            column=1,
            models=('readings.*',),
        ))

        # append an app list module for "Applications"
        self.children.append(modules.ModelList(
            _('Customers'),
            collapsible=True,
            column=1,
            models=('customers.*',),
        ))

        # Cache module
        self.children.append(CacheModule(
            _('Cache Status'),
            column=2,
        ))

        ## append another link list module for "support".
        #self.children.append(modules.LinkList(
        #    _('Media Management'),
        #    column=2,
        #    children=[
        #        {
        #            'title': _('FileBrowser'),
        #            'url': '/admin/filebrowser/browse/',
        #            'external': False,
        #        },
        #    ]
        #))
        #
        ## append another link list module for "support".
        #self.children.append(modules.LinkList(
        #    _('Support'),
        #    column=2,
        #    children=[
        #        {
        #            'title': _('Django Documentation'),
        #            'url': 'http://docs.djangoproject.com/',
        #            'external': True,
        #        },
        #        {
        #            'title': _('Grappelli Documentation'),
        #            'url': 'http://packages.python.org/django-grappelli/',
        #            'external': True,
        #        },
        #        {
        #            'title': _('Grappelli Google-Code'),
        #            'url': 'http://code.google.com/p/django-grappelli/',
        #            'external': True,
        #        },
        #    ]
        #))
        #
        ## append a feed module
        #self.children.append(modules.Feed(
        #    _('Latest Django News'),
        #    column=2,
        #    feed_url='http://www.djangoproject.com/rss/weblog/',
        #    limit=5
        #))
        #
        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=10,
            collapsible=False,
            column=3,
        ))
