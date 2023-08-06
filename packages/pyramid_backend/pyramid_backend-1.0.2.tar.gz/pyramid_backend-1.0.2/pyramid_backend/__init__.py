__author__ = 'tarzan'

import re
import importlib
from backend_manager import register_manager_factory

ADMIN_SITE_PATH = None

def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """
    global ADMIN_SITE_PATH
    settings = config.get_settings()
    ADMIN_SITE_PATH = settings['pyramid_backend.admin_site']
    ADMIN_SITE_PATH = ADMIN_SITE_PATH.strip('/') + '/'

    from . import resources as _rsr
    from . import model as model_helper
    from . import views

    route_pattern = ADMIN_SITE_PATH + '*traverse'
    config.add_route('admin_site', route_pattern, factory=_rsr.AdminSite)
    config.add_directive('add_model_view', views.add_model_view)
    config.add_directive('add_model_action', views.add_model_action)
    config.add_directive('add_object_action', views.add_object_action)

    factories_path = settings.get('pyramid_backend.manager_factories', """
    pyramid_backend.backend_manager.sqlalchemy.factory
    """)
    factories_path = filter(bool, re.split('\s+', factories_path))
    for factory in factories_path:
        if not callable(factory):
            _module, _var = factory.rsplit('.', 1)
            _module = importlib.import_module(_module, package=None)
            factory = getattr(_module, _var)

        register_manager_factory(factory(config))

    model_paths = settings.get('pyramid_backend.models', '')
    model_paths = filter(bool, re.split('\s+', model_paths))
    for path in model_paths:
        if '#' in path:
            path, actions = path.split('#', 1)
            actions = re.split(r'[\s,]+', actions.strip())
        else:
            actions = None
        _module, _var = path.rsplit('.', 1)
        _module = importlib.import_module(_module, package=None)
        model = getattr(_module, _var)
        config.add_model_view(model, actions=actions)

    config.scan(__name__)