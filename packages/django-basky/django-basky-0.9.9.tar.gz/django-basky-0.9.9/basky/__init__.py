version = (0, 9, 9)


def register(cls, **kwargs):
    from basky.config import BasketRegistry, BasketConfig
    # create a blank configuration
    config = kwargs.get('config', None)

    if config is None:
        config = BasketConfig()
        for k, v in kwargs.items():
            setattr(config, k, v)
    # generate a key for the class
    key = '%s_%s' % (cls._meta.app_label, cls._meta.module_name)
    # update the config with any kwargs
    # now add it to the registry
    BasketRegistry._registry[key] = config


# return a formatted version string
def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in version)


# do the autodiscover stuff
def autodiscover():
    """
    Auto discover brazenly copied from django.contrib.admin.
    """
    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from basky.config import BasketRegistry

    for app in settings.INSTALLED_APPS:
        try:
            import_module(app)
        except ImportError:
            pass
        # Attempt to import the app's basket module.
        try:
            before_import_registry = copy.copy(BasketRegistry._registry)
            import_module('%s.basket' % app)
        except ImportError:
            pass
        except Exception:
            BasketRegistry._registry = before_import_registry
