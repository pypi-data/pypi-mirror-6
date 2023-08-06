__author__ = 'tarzan'

from pyramid.view import view_config
from datetime import datetime
import inspect
from pyramid_backend import resources as _rsr
from pyramid_backend import model as model_helper
import venusian


@view_config(route_name='admin_site', context=_rsr.AdminSite,
             renderer='pyramid_backend:templates/index.mak')
def admin_site_home_view(request):
    """
    :type request: pyramid.request.Request
    """
    models = model_helper.get_registered_models()
    return {
        'models': [dict(
            name=m.__name__,
            url=model_helper.get_model_url(request, m)
        ) for m in models]
    }


def cell_datatype(val):
    if val is None:
        return 'none'
    if isinstance(val, bool):
        return 'bool'
    if isinstance(val, (int, long, float)):
        return 'number'
    if isinstance(val, datetime):
        return 'datetime'
    if isinstance(val, basestring):
        return 'longtext' if len(val) > 40 else 'text'
    if inspect.isclass(type(val)):
        return 'class'
    return 'generic'


from . import model_view
from .model_view import ModelView


def add_model_view(config, model, view_cls=None, actions=None):
    """
    :type config: pyramid.config.Configurator
    """
    model_helper.register_model(model)

    if view_cls is None:
        view_cls = ModelView
    mgr = model.__backend_manager__
    """:type : pyramid_backend.backend_manager.Manager"""
    if actions is None:
        actions = mgr.default_actions
    for action_conf in actions:
        action_name, action_conf = mgr.normalize_action(action_conf)
        if 'view' not in action_conf:
            action_conf['view'] = view_cls
        _add_action_view(config, model, action_name, **action_conf)


def _add_action_view(config, model, action_name, default_context=None, **kwargs):
    model_helper.register_model(model)
    mgr = model.__backend_manager__
    """:type : pyramid_backend.backend_manager.Manager"""
    if 'context' not in kwargs:
        kwargs['context'] = default_context
    if 'route_name' not in kwargs:
        kwargs['route_name'] = 'admin_site'
    if 'name' not in kwargs:
        kwargs['name'] = action_name
    action_name, action_conf = mgr.add_action((action_name, kwargs))
    view_conf = {k: v for k, v in action_conf.items() if not k.startswith('_')}
    config.add_view(**view_conf)


def add_model_action(config, model, action_name, **kwargs):
    model_helper.register_model(model)
    mgr = model.__backend_manager__
    _add_action_view(config, model, action_name, mgr.ModelResource, **kwargs)


def add_object_action(config, model, action_name, **kwargs):
    model_helper.register_model(model)
    mgr = model.__backend_manager__
    _add_action_view(config, model, action_name, mgr.ObjectResource, **kwargs)


class model_view_config(object):
    def __init__(self, model, actions=None):
        assert model, "You have to specify model"
        self.model = model
        self.actions = actions

    def view_config(self, scanner, name, ob):
        add_model_view(scanner.config,
                       self.model,
                       ob,
                       actions=self.actions)

    def __call__(self, wrapped):
        assert inspect.isclass(wrapped), \
            '@model_view_config can decorate to class only (decorated to %s)' % type(wrapped)
        info = venusian.attach(wrapped, self.view_config)
        return wrapped


class _action_view_config(object):
    _add_action_fn = None

    def __init__(self, model, name=None, **kwargs):
        assert model, "You have to specify model"
        self.model = model
        self.action_name = name
        self.conf = kwargs

    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            conf = self.conf.copy()
            conf['view'] = ob
            self.__class__._add_action_fn(scanner.config,
                             self.model,
                             self.action_name,
                             **conf)
        info = venusian.attach(wrapped, callback)
        if info.scope == 'class':
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if not self.conf.get('attr'):
                self.conf['attr'] = wrapped.__name__
        if self.action_name is None:
            self.action_name = wrapped.__name__
        return wrapped


class model_action_config(_action_view_config):
    _add_action_fn = staticmethod(add_model_action)


class object_action_config(_action_view_config):
    _add_action_fn = staticmethod(add_object_action)
