# core Python packages
import importlib


def installed_modules():
    """Check for installed modules and return list with relevant data
    """
    # detect presence/absence of component modules
    module_names = ['djhcup_core',
                    'djhcup_staging',
                    'djhcup_norm',
                    'djhcup_recomb']
    installed = {}

    for x in module_names:
        # TODO: Rewrite to pull version numbers for each of these as well
        try:
            module = importlib.import_module(x)
            installed[x] = True
        except ImportError:
            installed[x] = False
    
    if len(installed) > 0:
        return installed
    else:
        return False
