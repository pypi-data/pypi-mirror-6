pyramid_backend
===============

A backend development kit for pyramid, feel free to email me *hoc3010 at gmail dot com* about this package.

Usage
-----

    config.include('pyramid_backend')

### Configurations:

1. *pyramid_backend.admin_site*: related path for backend site from root
2. *pyramid_backend.manager_factories*: the list of backend manager factories. Default is :

        pyramid_backend.backend_manager.sqlalchemy:factory

3. *pyramid_backend.models*: list of class to be managed automatically by pyramid_backend

For each model, the display configurations can be:

    Model.__backend_schema_cls__ = a Colander/Deform Schema
    Model.__backend_slug__ = value to use on url, default = auto detect
    Model.__backend_display_name__ = display name for model, default = auto detect
    Model.__backend_id_attr__ = id attribute name, default = "id"
    Model.__backend_list__columns_to_display__ = List Attributes, default = auto detect
    Model.__backend_detail__columns_to_display__ = List Attributes, default = auto detect
    Model.__backend_list__items_per_page__ = Number of items per page, default = 50
    Model.__backend_detail__relations_to_display__ = List Attributes, default = auto detect

#### List Attributes

This is a list of attributes to display, each item can be:

1. a string: attribute name
2. a tuple: first element is attribute name. The rest is limit (if it's a list) and display name,
order is not important

#### Backend manager's configuration:

##### SQLAlchemy

1. *pyramid_backend.sqlalchemy.dbsession*: the full path to Session object

### API

> Updating

#### @model_view_config, add_model_view
#### @model_action_config, add_model_action
#### @object_action_config, add_object_action


CHANGE LOG
----------

### Version 1.0.x

* Initialize
