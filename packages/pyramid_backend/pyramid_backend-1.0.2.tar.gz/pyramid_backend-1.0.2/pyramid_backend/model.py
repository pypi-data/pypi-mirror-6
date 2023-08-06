__author__ = 'tarzan'

import inspect
from .backend_manager import create_backend_manager

_registered_models = [

]

def get_model_url(request, model, action=None):
    model = get_registered_model(model)
    traverse = [model.__backend_manager__.slug,]
    if action:
        traverse.append(action)
    return request.route_url('admin_site',
                             traverse=traverse)

def get_registered_models():
    return _registered_models

def get_registered_model(model):
    for m in _registered_models:
        if m is model:
            return m
    raise NotImplementedError('%s model has not been implemented' % model.__name__)

def is_registered_model(obj):
    if not inspect.isclass(obj):
        obj = type(obj)
        if not inspect.isclass(obj):
            return False
    return obj in _registered_models

def register_model(model):
    global _registered_models
    if model in _registered_models:
        return
    model.__backend_manager__ = create_backend_manager(model)
    _registered_models.append(model)