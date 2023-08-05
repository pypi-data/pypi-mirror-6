from app import app
from flask.ext.appbuilder.security.models import is_menu_public, is_item_public
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask import g, request, url_for
from flask.ext.login import current_user


def app_template_filter(filter_name=''):
    """
        Use this decorator to expose views in your view classes.
    """
    def wrap(f):
        if not hasattr(f, '_filter'):
            f._filter = filter_name
        return f
    return wrap


class TemplateFilters(object):
    
    def __init__(self, app):
        for attr_name in dir(self):
            if hasattr(getattr(self, attr_name),'_filter'):
                attr = getattr(self, attr_name)
                app.jinja_env.filters[attr._filter] = attr


    @app_template_filter('link_order')
    def link_order_filter(self, column, generalview_name):
        """
        Arguments are passed like: _oc_<VIEW_NAME>=<COL_NAME>&_od_<VIEW_NAME>='asc'|'desc'
        """
        new_args = request.view_args.copy()
        args = request.args.copy()
        if ('_oc_' + generalview_name) in args:
            args['_oc_' + generalview_name] = column
            if args.get('_od_' + generalview_name) == 'asc':
                args['_od_' + generalview_name] = 'desc'
            else:
                args['_od_' + generalview_name] = 'asc'
        else:
            args['_oc_' + generalview_name] = column
            args['_od_' + generalview_name] = 'asc'
        return url_for(request.endpoint,**dict(new_args.items() + args.to_dict().items()))


    @app_template_filter('link_page')
    def link_page_filter(self, page, generalview_name):
        """
        Arguments are passed like: page_<VIEW_NAME>=<PAGE_NUMBER>
        """
        new_args = request.view_args.copy()
        args = request.args.copy()
        args['page_' + generalview_name] = page
        return url_for(request.endpoint,**dict(new_args.items() + args.to_dict().items()))
                

    @app_template_filter('get_link_next')
    def get_link_next_filter(self, s):
        return request.args.get('next')

    # to improve
    @app_template_filter('set_link_filters')
    def set_link_filters_filter(self, path, filters, pk):
        lnkstr = path
        
        for _filter in filters:
            lnkstr = lnkstr + '&_flt_' + _filter + '=' + str(pk)
        return lnkstr        

    @app_template_filter('get_link_order')
    def get_link_order_filter(self, column, generalview_name):
        if request.args.get('_oc_' + generalview_name) == column:
            if (request.args.get('_od_' + generalview_name) == 'asc'):
                return 2
            else:
                return 1
        else:
            return 0

    @app_template_filter('get_attr')
    def get_attr_filter(self, obj, item):
        return getattr(obj, item)


    @app_template_filter('is_menu_visible')
    def is_menu_visible(self, item):
        if current_user.is_authenticated():
            if is_menu_public(item) or g.user.has_menu_access(item.name):
                return True
            else:
                return False
        else:
            if is_menu_public(item.name):
                return True
            else:
                return False

    @app_template_filter('is_item_visible')
    def is_item_visible(self, permission, item):
        if current_user.is_authenticated():
            if g.user.has_permission_on_view(permission, item):
                return True
            else:
                return False
        else:
            if is_item_public(permission, item):
                return True
            else:
                return False
