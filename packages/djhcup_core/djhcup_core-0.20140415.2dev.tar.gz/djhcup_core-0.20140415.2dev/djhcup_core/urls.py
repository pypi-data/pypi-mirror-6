# Django imports
from django.conf.urls import patterns, include, url


# local imports
import utils


# base patterns always available through having djhcup_core installed
urlpatterns = patterns('',
    url(r'^$', 'djhcup_core.views.index', name='index'),
)


# check for installed modules, and include url patterns from each
installed_mods = utils.installed_modules()


# tack on url patterns for installed component modules
# these are always prefixed by the module name e.g. /staging/batches/
for mod, installed in installed_mods.iteritems():
    
    # but don't add core urls (this file) again
    if installed is True and mod is not 'djhcup_core':
        prefix = mod.split('_')[-1]
        urlpatterns += patterns('',
                                url(r'^%s/' % prefix, include('%s.urls' % mod)),
                                )