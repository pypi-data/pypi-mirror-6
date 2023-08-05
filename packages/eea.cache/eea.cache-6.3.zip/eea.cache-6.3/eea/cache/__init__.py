""" EEA Cache package
"""
import os
import cPickle
import hashlib
from zope.interface import directlyProvides
from zope.component import queryUtility
from plone.memoize import volatile
from plone.memoize.interfaces import ICacheChooser
from plone.memoize.ram import AbstractDict
from plone.memoize.ram import store_in_cache
from eea.cache.utility import MemcachedClient
from eea.cache.interfaces import IMemcachedClient

try:
    from Products.CMFCore import interfaces
    IPropertiesTool = interfaces.IPropertiesTool
except ImportError:
    from zope.interface import Interface
    class IPropertiesTool(Interface):
        """ Fallback
        """

DEPENDENCIES = {'frontpage-highlights':
                    ['Products.EEAContentTypes.browser.frontpage.getHigh',
                     'Products.EEAContentTypes.browser.frontpage.getMedium',
                     'Products.EEAContentTypes.browser.frontpage.getLow'],
                'navigation':
                    ['Products.NavigationManager.NavigationManager.getTree', ],
                'eea.facetednavigation':
                    ['eea.facetednavigation.browser.app.query.__call__',
                     'eea.facetednavigation.browser.app.counter.__call__', ],
                'eea.sitestructurediff':
                    ['eea.sitestructurediff.browser.sitemap.data', ]}


class MemcacheAdapter(AbstractDict):
    """ Memcache Adapter
    """

    def __init__(self, client, globalkey=''):
        pt = queryUtility(IPropertiesTool)
        st = getattr(pt, 'site_properties', None)
        defaultLifetime = getattr(st, 'memcached_defaultLifetime',
                                  client.defaultLifetime)
        try:
            defaultLifetime = int(defaultLifetime)
        except Exception:
            defaultLifetime = client.defaultLifetime

        client.defaultLifetime = defaultLifetime
        self.client = client

        dependencies = []
        if globalkey:
            for k, v in DEPENDENCIES.items():
                if globalkey in v:
                    dependencies.append(k)

        self.dependencies = dependencies

    def _make_key(self, source):
        """ Make key
        """
        return hashlib.md5(source).hexdigest()

    def __getitem__(self, key):
        """ __getitem__
        """
        cached_value = self.client.query(self._make_key(key), raw=True)
        if cached_value is None:
            raise KeyError(key)
        else:
            return cPickle.loads(cached_value)

    def __setitem__(self, key, value, lifetime=None):
        """ __setitem__
        """
        cached_value = cPickle.dumps(value)
        self.client.set(cached_value,
                        self._make_key(key),
                        lifetime=lifetime,
                        raw=True,
                        dependencies=self.dependencies)


def frontpageMemcached():
    """ Frontpage Memcached
    """
    servers = os.environ.get("MEMCACHE_SERVER",
                             "127.0.0.1:11211").split(",")
    return MemcachedClient(servers, defaultNS=u'frontpage')


def choose_cache(fun_name):
    """ Choose cache
    """
    client = queryUtility(IMemcachedClient)
    return MemcacheAdapter(client, globalkey=fun_name)


directlyProvides(choose_cache, ICacheChooser)

_marker = object()


def cache(get_key, dependencies=None, lifetime=None):
    """ Cache
    """

    def decorator(fun):
        """ Decorator
        """

        def replacement(*args, **kwargs):
            """ Replacement
            """
            if dependencies is not None:
                for d in dependencies:
                    deps = DEPENDENCIES.get(d, [])
                    method = "%s.%s" % (fun.__module__, fun.__name__)
                    if method not in deps:
                        deps.append(method)
                        DEPENDENCIES[d] = deps
            try:
                key = get_key(fun, *args, **kwargs)
            except volatile.DontCache:
                return fun(*args, **kwargs)
            key = '%s.%s:%s' % (fun.__module__, fun.__name__, key)
            cache_store = store_in_cache(fun, *args, **kwargs)
            cached_value = cache_store.get(key, _marker)
            if cached_value is _marker:
                cached_value = fun(*args, **kwargs)
                # plone.memoize doesn't have the lifetime keyword parameter
                # like eea.cache does so we check for the module name
                if 'eea.cache' in cache_store.__module__:
                    cache_store.__setitem__(key, cached_value,
                                                            lifetime=lifetime)
                else:
                    cache_store.__setitem__(key, cached_value)

            return cached_value

        return replacement

    return decorator
