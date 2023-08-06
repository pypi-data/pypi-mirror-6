# core Python packages
import logging


# third party packages


# django packages
from django.shortcuts import render
from django.utils.timezone import utc


# local imports
import utils

# start a logger
logger = logging.getLogger('default')


# Create your views here.
def index(request):
    logger.debug('Core index requested')
    
    installed_modules = utils.installed_modules()
    
    logger.debug('Component modules detected:')
    [logger.debug('%s: %s' % (k, v)) for k, v in installed_modules.iteritems()]

    context = {
        'title': 'The Django-HCUP Hachoir: Core Index', 
        'djhcup_components': installed_modules,
        }
    
    template = 'djhcup_core_index.html'
    return render(request, template, context)

