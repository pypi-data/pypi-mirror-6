__author__ = 'tarzan'

import urllib
from . import model as model_helper
import pyramid_backend as pb


def model_url(request, model, action=None, query=None):
    """
    Get url for an model with its action
    :type request: pyramid.request.Request
    :type model: object
    :type action: string
    :type query: string or dict
    """
    model = model_helper.get_registered_model(model)

    url = pb.ADMIN_SITE_PATH + model.__backend_manager__.slug
    if action:
        url += '/' + action
    if query and isinstance(query, dict):
        query = urllib.urlencode(query)
    if query:
        url += '?' + query
    return request.relative_url(url, True)


def object_url(request, obj, action=None, query=None):
    if not obj:
        return ''
    if isinstance(obj, type):
        model = obj
    else:
        model = obj.__class__
    obj_id = model.__backend_manager__.object_id(obj)
    url = pb.ADMIN_SITE_PATH + model.__backend_manager__.slug + '/' + str(obj_id)
    if action:
        url += '/' + action
    if query and isinstance(query, dict):
        query = urllib.urlencode(query)
    if query:
        url += '?' + query
    return request.relative_url(url, True)


class ModelResource(object):
    model = None

    def __init__(self, parent, name):
        """
        :type parent: AdminSite
        """
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request

    @property
    def backend_mgr(self):
        """
        :rtype : pyramid_backend.backend_manager.Manager
        """
        return self.model.__backend_manager__

    def __getitem__(self, id_value):
        obj = self.backend_mgr.find_object(id_value)
        if obj:
            return self.backend_mgr.ObjectResource(self, id_value, obj)
        raise KeyError('%s#%s not found' % (self.backend_mgr.display_name, id_value))

    def __resource_url__(self, *args, **kwargs):
        return model_url(self.request, self.model)

    def __unicode__(self):
        return unicode(self.model.__name__)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class ObjectResource(object):
    url = '#'

    def __init__(self, parent, name, object):
        """
        :type parent: ModelResource
        """
        self.__parent__ = parent
        self.__name__ = name
        self.model = parent.model
        self.request = parent.request
        self.object = object

    def __resource_url__(self, *args, **kwargs):
        return object_url(self.request, self.object)

    def __unicode__(self):
        return u'%s' % self.object

    def __str__(self):
        return self.__unicode__().encode('utf-8')


_AUTO_CLASSES = {}


def model_resource_class(model):
    cls_name = model.__name__ + '_ModelResource'
    if cls_name not in _AUTO_CLASSES:
        _AUTO_CLASSES[cls_name] = type(cls_name, (ModelResource,), {
            'model': model,
        })

    try:
        _AUTO_CLASSES[cls_name].__acl__ = model.__backend_manager__.__acl__
    except AttributeError:
        pass

    return _AUTO_CLASSES[cls_name]


def object_resource_class(model):
    cls_name = model.__name__ + '_ObjectResource'
    if cls_name not in _AUTO_CLASSES:
        _AUTO_CLASSES[cls_name] = type(cls_name, (ObjectResource,), {
            'model': model,
        })

    return _AUTO_CLASSES[cls_name]


class AdminSite(object):
    __acl__ = [
    ]
    model_mappings = {

    }

    __parent__ = None
    __name__ = ''
    # @property
    # def __name__(self):
    #     return pb.ADMIN_SITE_PATH.strip('/')

    def __init__(self, request):
        """
        :type request: pyramid.request.Request
        """
        self.request = request

    def __getitem__(self, item):
        try:
            model = AdminSite.model_mappings[item]
        except KeyError as e:
            for model in model_helper.get_registered_models():
                if model.__backend_manager__.slug == item:
                    AdminSite.model_mappings[item] = model
                    break
            else:
                raise e
        return model.__backend_manager__.ModelResource(self, item)

    def __resource_url__(self, *args, **kwargs):
        return self.request.application_url + '/' + pb.ADMIN_SITE_PATH.strip('/') + '/'

    def __unicode__(self):
        return u'Backend'

    def __str__(self):
        return 'Backend'
