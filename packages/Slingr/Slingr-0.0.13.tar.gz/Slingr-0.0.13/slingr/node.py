# -*- coding: utf-8 -*-
"""
Build an application
"""

from __future__ import absolute_import
from collections import OrderedDict

import pystache

from slingr import app
from slingr.common import (
    get_immediate_subdirectories, itersubclasses, ospath, shortname, splice,
    uniquify, write_file, LocalTimeFormat)
from slingr.coburl import CobUrl, pathjoin
from slingr.config import _Config, NodeConfig, ProfilesConfig
from slingr.asset  import (
    AssetBundle, CssBundle, HtmlSheaf, HtmlTemplate, ImageBundle,
    JavaScriptBundle, LangSheaf, PathVal, StaticBundle, TemplateSheaf)


# Nodes

class NodeMap(OrderedDict):
    """Dict mapping node shortnames to nodes"""
    # Order of declaration matters, hence OrderedDict
    @classmethod
    def make(cls, nodes):
        return cls((node.shortname, node) for node in nodes)

    def names(self):
        return [node.shortname for node in self.itervalues()]

    def __repr__(self):
        return "<%s %s>" % (
            self.__class__.__name__, super(NodeMap, self).__repr__())

    def serialize(self):
        return OrderedDict(
            (name, [node.__class__.__name__, node.serialize()])
            for name, node in self.iteritems())

    # Note: _FactoryMap must be explicitly computed in deserialize()
    # after all derived classes are defined.
    _FactoryMap = None

    @classmethod
    def deserialize(cls, context, dct):
        if NodeMap._FactoryMap is None:
            NodeMap._FactoryMap = dict(
                (c.__name__, c) for c in itersubclasses(Node))
        return cls(
            (name, NodeMap._FactoryMap[cls_name].deserialize(context, value))
            for name, (cls_name, value) in dct.iteritems())

    @property
    def pathvals(self):
        return splice([node.pathvals for node in self.itervalues()])


class Node(object):
    """A Page or a View, which owns assets such as CSS, JS, etc"""
    AssetKinds = {
        'css':  CssBundle,
        'html': HtmlSheaf,
        'template': TemplateSheaf,
        'img':  ImageBundle,
        'js':   JavaScriptBundle,
        'lang': LangSheaf,
    }
    NamePrefix = '_node'
    Attrs = AssetKinds.keys()
    AuxAttrs = {}

    @staticmethod
    def clear_cache():
        Node.Cache = {}

    @classmethod
    def _load_node(
            cls, coburl, path='', prefix=None, profile=None,
            config=None, **kwargs):
        """Factory method, called from cls.load()"""
        node_name = cls.make_name(path, prefix, kwargs.get('name'))
        key = (node_name, profile)
        node = Node.Cache.get(key)
        if node is None:
            node_coburl = coburl.join(path)
            node_shortname = shortname(path)
            node_config = config or cls.load_config(coburl, path, profile)
            attrs = dict(
                (attr, asset_cls.load_sheaf(
                    node_name, node_coburl, path, node_config))
                for attr, asset_cls in cls.AssetKinds.iteritems())
            node = cls(node_coburl, node_name, node_shortname, profile,
                       node_config, **attrs)
            Node.Cache[key] = node
        return node

    load = _load_node

    def __init__(self, coburl, name, shortname, profile, config, **attrs):
        self.coburl, self.name, self.shortname, self.profile, self.config = (
            coburl, name, shortname, profile, config)
        for attr, value in attrs.iteritems():
            setattr(self, attr, value)

    def __repr__(self):
        return "<%s name=%r, coburl=%r, profile=%r, config=%r, %s>" % (
            self.__class__.__name__,
            self.name,
            self.coburl,
            self.profile,
            self.config.coburl,
            ", ".join("%s=%r" % (attr, getattr(self, attr, []))
                      for attr in self.Attrs))

    def __eq__(self, other):
        return (self.coburl == other.coburl
                and self.name == other.name
                and self.shortname == other.shortname
                and self.profile == other.profile
                and self.config == other.config
                and all((getattr(self, attr)
                            == getattr(other, attr))
                        for attr in self.Attrs)
                and all((getattr(self, attr, None)
                            == getattr(other, attr, None))
                        for attr in self.AuxAttrs)
                )

    def serialize(self):
        dct = dict(
            coburl=self.coburl.serialize(),
            name=self.name,
            shortname=self.shortname,
            profile=self.profile,
            config=self.config.serialize(),
        )
        for attr in self.Attrs + self.AuxAttrs.keys():
            value = getattr(self, attr, None)
            if value is not None:
                dct[attr] = value.serialize()
        return dct

    @classmethod
    def deserialize(cls, context, dct):
        attrs = dict((attr, asset_cls.deserialize(context, dct[attr]))
                     for attr, asset_cls in cls.AssetKinds.items())
        attrs.update(dict((attr, attr_cls.deserialize(context, dct[attr]))
                          for attr, attr_cls in cls.AuxAttrs.items()
                          if attr in dct))
        return cls(
            CobUrl.deserialize(context, dct['coburl']),
            dct['name'],
            dct['shortname'],
            dct['profile'],
            _Config.deserialize(context, dct['config']),
            **attrs)

    @classmethod
    def load_config(cls, coburl, path, profile):
        return (cls.load_profile_config(coburl, path, profile)
                or cls.load_node_config(coburl, path))

    @classmethod
    def load_profile_config(cls, coburl, path, profile):
        """Load Config for ``profile``, if it exists"""
        return ProfilesConfig.load(coburl, path, profile, file_required=False)

    @classmethod
    def load_node_config(cls, coburl, path):
        return NodeConfig.load(coburl, path)

    @classmethod
    def make_name(cls, path, prefix, name=None):
        """Create a unique, human-friendly name for this Node"""
        return name or "%s.%s" % (prefix or cls.NamePrefix, shortname(path))

    @classmethod
    def find_node_dirs(cls, coburl, path=''):
        dir = coburl.join(path, cls.DirName).abspath
        return get_immediate_subdirectories(dir) if ospath.isdir(dir) else []

    @classmethod
    def node_path(cls, name, path=''):
        return pathjoin(path, cls.DirName, name)

    @classmethod
    def load_nodes(cls, coburl, path='', names_and_prefixes=None,
                   default_prefix=None, profile=None, search=False):
        """Create all nodes found at coburl/path/DirName.

        :param coburl: CobUrl
        :param path:   directory path relative to coburl
        :param names_and_prefixes:  if supplied, load these;
                                    otherwise, load all.
        :param default_prefix:  Fall back to this
        :returns:      NodeMap
        """
        if not names_and_prefixes and search:
            names_and_prefixes = [(nd, default_prefix)
                                  for nd in cls.find_node_dirs(coburl, path)]
        names_and_prefixes = uniquify(names_and_prefixes or [])
        nodes = [cls.load(coburl, cls.node_path(node_dir), prefix, profile)
                 for node_dir, prefix in names_and_prefixes]
        return NodeMap.make(nodes)

    @property
    def pathvals(self):
        rv = [PathVal.make(self.coburl)]
        for attr in self.Attrs + self.AuxAttrs.keys():
            value = getattr(self, attr, None)
            if value is not None:
                rv.extend(value.pathvals)
        return rv

    def augment_sheaves(self, nodemap, prepend=True):
        """Prepend or append JS (CSS) references from view-nodemap's JS (CSS)
        to this node's JS (CSS), etc."""
        method = 'prepend' if prepend else 'append'
        for kind in ('css', 'js'):
            kind_attr = getattr(self, kind)
            kind_pathvals = splice([getattr(node, kind).pathvals
                                    for node in nodemap.values()])
            getattr(kind_attr, method)(kind_pathvals)
        return nodemap

    def _html_templates(self):
        return self.template.templates + self.html.templates

    html_templates = _html_templates  # Public function is overrideable

    def compute_html_templates(self):
        template_tree = HtmlTemplate.make_template_tree()
        for template in self.html_templates():
            template.compute(self.profile, template_tree)
        return template_tree

    def compile(self, global_node, options):
        self.compiled = CompiledNode(self, global_node)
        self.compiled.compile()


class _View(Node):
    """Common implementation of View"""
    DirName = 'views'
    NamePrefix = 'view'


class View(_View):
    """Top-level view"""


class PageView(_View):
    """View owned by a Page"""


class ExternalView(_View):
    """View imported from another package"""
    # TODO


class _PrimaryNode(Node):
    def html_templates(self):
        return self._html_templates() + self.view_templates()

    def view_templates(self):
        return splice([view.html_templates() for view in self.views.values()])


class GlobalNode(_PrimaryNode):
    """Owns top-level HTML templates, etc"""
    NamePrefix = 'global'
    AuxAttrs = {
        'base_template': HtmlTemplate,
        'views': NodeMap,
        'static': StaticBundle,
#       'mimetypes': ?,
    }

    @classmethod
    def load(cls, coburl, path='', prefix=None, profile=None,
             config=None, **kwargs):
        node = cls._load_node(
            coburl, path, prefix, profile, config, **kwargs)
        node.base_template = None
        base_template = getattr(node.config.data, 'baseTemplate', None)
        if base_template:
            node.base_template = HtmlTemplate.load(
                '',
                PathVal.make(node.coburl.join("html", base_template)),
                node.config)
        node.views = node.load_views()
        js2 = JavaScriptBundle.load_sheaf(
            node.name, node.coburl, path, node.config, 'js2')
        if js2:
            node.js.append(js2.pathvals)
        node.static = StaticBundle.load_sheaf(
            node.name, node.coburl, path, node.config, 'static')
        return node

    def load_views(self):
        """Load top-level Views"""
        views = View.load_nodes(
            self.coburl, names_and_prefixes=self.load_view_names())
        return self.augment_sheaves(views, prepend=False)

    def load_view_names(self):
        try:
            views = self.config.data.views
        except AttributeError:
            app.logger.warning(
                "No 'views' in config '%s'", self.config.coburl.path)
            views = []
        return [(name, View.NamePrefix) for name in views]

    @classmethod
    def load_with_config(cls, coburl, path="", filename="cob"):
        """Load top-level Cob-wide config"""
        config = NodeConfig.load(coburl, path=path, filename=filename)
        return cls.load(coburl, config=config, name=cls.NamePrefix)


class IndexPage(object):
    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return "<%s content=%r>" % (
            self.__class__.__name__,
            self.content
        )

    def __eq__(self, other):
        return (self.content == other.content)

    def serialize(self):
        return {
            "content": self.content,
        }

    @classmethod
    def deserialize(cls, context, dct):
        return cls(dct['content'])

    def write(self, output_path, reldir, filename='index.html'):
        path = pathjoin(output_path, reldir, filename)
        write_file(path, self.content)

    @property
    def pathvals(self):
        return []


class Page(_PrimaryNode):
    DirName = 'pages'
    NamePrefix = 'page'
    AuxAttrs = {
        'views': NodeMap,
        'index_page': IndexPage,
    }

    @classmethod
    def load(cls, coburl, path='', prefix=None, profile=None,
             config=None, **kwargs):
        node = cls._load_node(
            coburl, path, prefix, profile, config, **kwargs)
        node.views = node.load_views(prefix)
        return node

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        self.invalidation = None

    def __repr__(self):
        inv = self.invalidation
        return ("<%s name=%r, profile=%r, coburl=%r, " +
                "config=%r, views=%r, invalidation=%s>") % (
            self.__class__.__name__,
            self.name,
            self.profile,
            self.coburl,
            self.config.coburl,
            self._view_names(),
            inv.strftime(LocalTimeFormat) if inv else 0,
        )

    def invalidate(self, now):
        self.invalidation = now

    def load_views(self, prefix):
        view_prefix = (prefix or self.name) + "._view"
        views = PageView.load_nodes(
            self.coburl, self.coburl.path,
            self.view_names(view_prefix),
            view_prefix, self.profile)
        return self.augment_sheaves(views, prepend=True)

    def view_names(self, view_prefix):
        names = (self.profile_view_names(
                    self.coburl, self.coburl.path, self.profile)
                 or self.config_view_names(self.config))
        return [(name, View.NamePrefix
                    if CobUrl.is_absolute_path(name)
                    else view_prefix)
                for name in names]

    def _view_names(self):
        if hasattr(self, 'views') and hasattr(self.views, 'names'):
            return self.views.names()
        else:
            return None

    @classmethod
    def profile_view_names(cls, coburl, path, profile):
        pc = cls.load_profile_config(
                coburl, pathjoin(path, "views"), profile)
        return pc and pc.data.views

    @classmethod
    def config_view_names(cls, config):
        return getattr(config.data, 'views', [])

    @classmethod
    def make_profile(cls, coburl, page_name, profile, prefix=None):
        """Factory: Create a Page for a specific ``profile``"""
        rv = cls.load(coburl, cls.node_path(page_name), prefix, profile)
        rv.page_name = page_name
        return rv

    def output_dir(self):
        return pathjoin(self.coburl.path, self.profile)


# CompiledNode

class CompiledNode(object):
    """Compiled Assets for a Node"""
    # TODO: serialize as part of page_profile in CobState

    JS_RenderFile = 'global.js'
    JS_PreambleFile = 'templates.js'
    CSS_RenderFile = 'style.css'

    def __init__(self, node, global_node):
        self.node, self.global_node = node, global_node

    def __repr__(self):
        return ("<%s node=%s, css=%r, html=%r, img=%r, "
                "js=%r, lang=%r, context=%r>") % (
                self.__class__.__name__,
                self.node.name,
                getattr(self, 'css', None),
                getattr(self, 'html', None),
                getattr(self, 'img', None),
                getattr(self, 'js', None),
                getattr(self, 'lang', None),
                getattr(self, 'context', None))

    def compile(self):
        self.compile_css()
        self.compile_html()
        self.compile_img()
        self.compile_js()
        self.compile_lang()

    def compile_css(self):
        self.css = self.node.css.resolve_contents(
            self.node.coburl.cobroot.env)

    def compile_html(self):
        self.html = self.node.compute_html_templates()

    def compile_img(self):
        self.img = self.node.img.resolve_contents(
            self.node.coburl.cobroot.env)

    def compile_js(self):
        self.js = self.node.js.resolve_contents(
            self.node.coburl.cobroot.env)

    def compile_lang(self):
        self.lang = None # TODO

    def template_wrapper(
            self, root='window', app_namespace='ns',
            template_namespace='_templates'):
        obj   = root + '.' + app_namespace
        wrap  = obj + ' = ' + obj + ' || {};\n'
        obj  += '.' + template_namespace
        wrap += obj + ' = ' + obj + ' || {};\n'
        return "{0}$.extend(true, {1}, {2});\n".format(
            wrap, obj, self.html.as_json())

    @classmethod
    def op_assets_to_includes(
            cls, op_assets,
            cdn_root, output, reldir, use_querystring, bundle_cls):
        def template_data(an):
            url = pathjoin(
                cdn_root + '/' + output,
                an.target + (an.query_string() if use_querystring else ''))
            if an.source:
                return an.source.template_dict(url)
            else:
                # No source => Preamble or CombineTarget
                return bundle_cls.template_dict(url)
        return [template_data(an)
                for op, an in op_assets
                if op != AssetBundle.Ops.Combine]

    def get_css_includes(
            self, cdn_root, output, reldir, use_querystring=True):
        """Explicitly included CSS files, after compiling,
        minification, etc."""
        return (
            self.op_assets_to_includes(
                self.global_node.css_op_assets,
                cdn_root, output, reldir, use_querystring, CssBundle)
            +
            self.op_assets_to_includes(
                self.node.css_op_assets,
                cdn_root, output, reldir, use_querystring, CssBundle)
        )

    def get_js_includes(
            self, cdn_root, output, reldir, use_querystring=True):
        """Explicitly included JS files, after compiling,
        minification, etc."""
        # TODO: allow async, defer etc attributes
        return (
            self.op_assets_to_includes(
                self.global_node.js_op_assets,
                cdn_root, output, reldir, use_querystring, JavaScriptBundle)
            +
            self.op_assets_to_includes(
                self.node.js_op_assets,
                cdn_root, output, reldir, use_querystring, JavaScriptBundle)
        )

    def build_head(self):
        title = "Fixme Title" # TODO: pull from lang
        return title

    def get_page_name(self):
        return self.node.shortname

    def render_page(self, output_path, output, reldir, cdn_root):
        index_page, context = None, None

        if self.node.template.templates:
            context = {
                'title':       self.build_head(),
                'pageName':    self.get_page_name(),
                'profilePage': reldir,
                'cssInc':      self.get_css_includes(cdn_root, output, reldir),
                'jsInc':       self.get_js_includes( cdn_root, output, reldir),
                'bodyContent': self.node.template.templates[0].data,
            }
            if self.global_node.base_template:
                page_template = self.global_node.base_template.data
                index_page = IndexPage(
                    pystache.render(page_template, context))
        return index_page, context

    def emit(self, filecache, output_path, output, reldir, options):
        concatenate = options.get('concatenate', True)
        use_symlink = options.get('use_symlink', False)
        # e.g., "<% &cdn_root %>" for runtime eval
        cdn_root = options.get('cdn_root', '')

        js_premable = self.template_wrapper()
        self.node.js_op_assets = self.node.js.compute_op_assets(
            self.node.coburl, reldir, self.JS_RenderFile, concatenate,
            js_premable, self.JS_PreambleFile)
        self.node.js.emit_assets(
            filecache, output_path, self.node.js_op_assets,
            js_premable, use_symlink=use_symlink)

        self.node.css_op_assets = self.node.css.compute_op_assets(
            self.node.coburl, reldir, self.CSS_RenderFile, concatenate)
        self.node.css.emit_assets(
            filecache, output_path, self.node.css_op_assets,
            use_symlink=use_symlink)

        self.node.img.emit_assets(
            filecache, output_path,
            self.node.img.compute_op_assets(self.node.coburl, reldir),
            use_symlink=use_symlink)

        if hasattr(self.node, 'static'):
            # FIXME
            self.node.static.emit_assets(
                filecache, output_path,
                self.node.static.compute_op_assets(self.node.coburl, reldir),
                use_symlink=use_symlink)

        self.index_page, self.context = self.render_page(
            output_path, output, reldir, cdn_root)
        if self.index_page:
            self.index_page.write(output_path, reldir, 'index.html')
        return self.index_page
