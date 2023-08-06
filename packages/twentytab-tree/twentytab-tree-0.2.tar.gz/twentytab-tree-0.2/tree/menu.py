from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


def prepare_nodes(nodes, request):
    for node in nodes:
        if node.slugable:
            if node.show_if_logged and request.user and (
                not node.groups.all() or node.groups.filter(
                    pk__in=request.user.groups.values_list('pk', flat=True).all()
                )
            ):
                    node.hide_in_navigation = True

            try:
                node.alias = node.transnode.alias
            except:
                node.alias = node.name
            node.url = None
            if node.page and not node.value_regex:
                node.url = u"/{}".format(node.slug)
    return nodes


class Menu(object):
    """
    This class provides some tools to create and render tree structure menu in according to nodes' structure
    created for your application.
    It takes some arguments:
    - request: simply http request
    - root: the root of menu (it's hidden in menu string)
    - upy_context: it contains informations about current page and node
    - menu_depth: it's depth level for menu introspection
    - view_hidden: if True then hidden nodes will be shown
    - g11n_depth: check g11n_depth in contrib.g11n.models documentation
    """

    def __init__(self, request, root, upy_context, menu_depth=0, view_hidden=False):
        self.request = request
        self.upy_context = upy_context
        self.root = root
        self.menu_depth = menu_depth
        self.view_hidden = view_hidden

    def __do_menu(self, menu_as, current_linkable=False, class_current="",
                  chars="", before_1="", after_1="", before_all="",
                  after_all="", render=True):
        nodes = self.root.get_descendants()
        list_nodes = prepare_nodes(list(nodes), self.request)

        if not render:
            return list_nodes

        if self.menu_depth != 0:
            relative_depth = self.menu_depth + self.root.level
        else:
            relative_depth = 0

        return render_to_string('tpl/menu_%s.tpl.html' % menu_as,
                                {'NODE': self.upy_context['NODE'], 'nodes': list_nodes, 'chars': chars,
                                 'current_linkable': current_linkable,
                                 'menu_depth': relative_depth, 'class_current': class_current,
                                 'view_hidden': self.view_hidden, 'before_1': before_1,
                                 'after_1': after_1, 'before_all': before_all, 'after_all': after_all,
                                }, context_instance=RequestContext(self.request))

    def as_ul(self, current_linkable=False, class_current="active_link",
              before_1="", after_1="", before_all="", after_all=""):
        """
        It returns menu as ul
        """
        return self.__do_menu("as_ul", current_linkable, class_current,
                              before_1=before_1, after_1=after_1, before_all=before_all, after_all=after_all)

    def as_p(self, current_linkable=False, class_current="active_link"):
        """
        It returns menu as p
        """
        return self.__do_menu("as_p", current_linkable, class_current)

    def as_string(self, chars, current_linkable=False, class_current="active_link"):
        """
        It returns menu as string
        """
        return self.__do_menu("as_string", current_linkable, class_current, chars)

    def as_tree(self):
        """
        It returns a menu not cached as tree
        """
        return self.__do_menu("", render=False)


class Breadcrumb(object):
    """
    This class provides some tools to create and render tree structure breadcrumb in according to nodes' structure
    created for your application.
    It takes some arguments:
    - request: simply http request
    - leaf: the the leaf of breadcrumb (it's hidden in menu string)
    - upy_context: it contains informations about current page and node
    - view_hidden: if True then hidden nodes will be show
    - g11n_depth: check g11n_depth in contrib.g11n.models documentation
    """

    def __init__(self, request, leaf, upy_context, view_hidden=False):
        self.request = request
        self.leaf = leaf
        self.upy_context = upy_context
        self.view_hidden = view_hidden

    def __do_menu(self, menu_as, show_leaf, current_linkable, class_current, chars="", render=True):
        nodes = self.leaf.get_ancestors()[1:]
        list_nodes = list(nodes)
        if show_leaf:
            list_nodes.append(self.leaf)

        list_nodes = prepare_nodes(list_nodes, self.request)

        if not render:
            return list_nodes

        menutpl = render_to_string('tpl/breadcrumb_%s.tpl.html' % menu_as,
                                   {'NODE': self.upy_context['NODE'], 'nodes': list_nodes, 'chars': chars,
                                    'current_linkable': current_linkable,
                                    'class_current': class_current,
                                    'view_hidden': self.view_hidden}, context_instance=RequestContext(self.request))

        return mark_safe(menutpl)

    def as_ul(self, show_leaf=True, current_linkable=False, class_current="active_link"):
        """
        It returns breadcrumb as ul
        """
        return self.__do_menu("as_ul", show_leaf, current_linkable, class_current)

    def as_p(self, show_leaf=True, current_linkable=False, class_current="active_link"):
        """
        It returns breadcrumb as p
        """
        return self.__do_menu("as_p", show_leaf, current_linkable, class_current)

    def as_string(self, chars, show_leaf=True, current_linkable=False, class_current="active_link"):
        """
        It returns breadcrumb as string
        """
        return self.__do_menu("as_string", show_leaf, current_linkable, class_current, chars)

    def as_tree(self):
        """
        It returns a menu not cached as tree
        """
        return self.__do_menu("", render=False)