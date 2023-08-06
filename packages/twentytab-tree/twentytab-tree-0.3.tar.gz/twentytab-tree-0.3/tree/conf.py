from appconf import AppConf
from django.conf import settings
import os


class TreeConf(AppConf):
    STATIC_URL = u'/static/'
    TREE_EDITOR_INCLUDE_ANCESTORS = False
    TREE_EDITOR_OBJECT_PERMISSIONS = False
    USE_GLOBAL_TEMPLATES_DIR = True
    DISALLOW_ALL_ROBOTS = True
    JQUERY_LIB = u"{}{}".format(
        getattr(settings, u'STATIC_URL', u'/static/'),
        u"tree/js/jquery-2.1.0.min.js"
    )
    JQUERYUI_LIB = u"{}{}".format(
        getattr(settings, u'STATIC_URL', u'/static/'),
        u"tree/js/jquery-ui-1.10.4.custom.min.js"
    )
    JQUERYUI_CSSLIB = u"{}{}".format(
        getattr(settings, u'STATIC_URL', u'/static/'),
        u"tree/css/smoothness/jquery-ui-1.10.4.custom.min.css"
    )

    def configure_static_url(self, value):
        if not getattr(settings, 'STATIC_URL', None):
            self._meta.holder.STATIC_URL = value
            return value
        return getattr(settings, 'STATIC_URL')

    def configure_tree_editor_include_ancestors(self, value):
        if not getattr(settings, 'TREE_EDITOR_INCLUDE_ANCESTORS', None):
            self._meta.holder.TREE_EDITOR_INCLUDE_ANCESTORS = value
            return value
        return getattr(settings, 'TREE_EDITOR_INCLUDE_ANCESTORS')

    def configure_tree_editor_object_permission(self, value):
        if not getattr(settings, 'TREE_EDITOR_OBJECT_PERMISSIONS', None):
            self._meta.holder.TREE_EDITOR_OBJECT_PERMISSIONS = value
            return value
        return getattr(settings, 'TREE_EDITOR_OBJECT_PERMISSIONS')

    def configure_use_global_templates_dir(self, value):
        res = getattr(settings, 'USE_GLOBAL_TEMPLATES_DIR', None)
        if not res:
            self._meta.holder.USE_GLOBAL_TEMPLATES_DIR = value
            res = value
        if res and not os.path.exists(u"{}/{}".format(os.getcwd(), 'templates')):
            os.mkdir(u"{}/{}".format(os.getcwd(), 'templates'))
        if res:
            list_dirs = ['templates']
            list_dirs.extend(
                list([u"templates/{}".format(tdir) for tdir in os.listdir(u"{}/{}".format(os.getcwd(), 'templates'))])
            )
            if getattr(settings, 'TEMPLATE_DIRS', None):
                self._meta.holder.TEMPLATE_DIRS = getattr(settings, 'TEMPLATE_DIRS').extends(list_dirs)
            else:
                self._meta.holder.TEMPLATE_DIRS = list_dirs
        return res

    def configure_disallow_all_robots(self, value):
        if not getattr(settings, 'DISALLOW_ALL_ROBOTS', None):
            self._meta.holder.DISALLOW_ALL_ROBOTS = value
            return value
        return getattr(settings, 'DISALLOW_ALL_ROBOTS')

    def configure_jquery_lib(self, value):
        if not getattr(settings, 'JQUERY_LIB', None):
            self._meta.holder.JQUERY_LIB = value
            return value
        return getattr(settings, 'JQUERY_LIB')

    def configure_jqueryui_lib(self, value):
        if not getattr(settings, 'JQUERYUI_LIB', None):
            self._meta.holder.JQUERYUI_LIB = value
            return value
        return getattr(settings, 'JQUERYUI_LIB')

    def configure_jqueryui_csslib(self, value):
        if not getattr(settings, 'JQUERYUI_CSSLIB', None):
            self._meta.holder.JQUERYUI_CSSLIB = value
            return value
        return getattr(settings, 'JQUERYUI_CSSLIB')

    def configure(self):
        if not getattr(settings, 'MIDDLEWARE_CLASSES', None):
            self._meta.holder.MIDDLEWARE_CLASSES = ['tree.middleware.upy_context.SetUpyContextMiddleware']
        else:
            middleware = getattr(settings, 'MIDDLEWARE_CLASSES')
            middleware.append('tree.middleware.upy_context.SetUpyContextMiddleware')
            self._meta.holder.MIDDLEWARE_CLASSES = middleware
        if not getattr(settings, 'TEMPLATE_CONTEXT_PROCESSORS', None):
            self._meta.holder.TEMPLATE_CONTEXT_PROCESSORS = ['tree.template_context.context_processors.set_meta']
        else:
            middleware = getattr(settings, 'TEMPLATE_CONTEXT_PROCESSORS')
            middleware.append('tree.template_context.context_processors.set_meta')
            self._meta.holder.TEMPLATE_CONTEXT_PROCESSORS = middleware
        return self.configured_data