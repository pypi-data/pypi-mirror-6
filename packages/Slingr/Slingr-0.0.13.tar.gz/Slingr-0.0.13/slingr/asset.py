# -*- coding: utf-8 -*-
"""
Build an application
"""

from __future__ import absolute_import

import hashlib
import json

import webassets

from slingr import app
from slingr.common import (
    enum, format_seconds, hashfile, hash_filename, itersubclasses,
    modification_time, read_file, shortname, Struct, write_file,
)
from slingr.coburl import CobUrl, pathjoin


# PathVals

class PathVal(object):
    """A path + possible associated values.

    Assets and pages have a list of associated entries (pathvals).
    At its simplest, a pathval is just a CobUrl,
    but it may have other data associated with it.

    For example:
        css:
        - foo.scss
        - /bar/fly.css
        - {url: /account/print.css, media: print}
        - url: /mobile/login-small.css
          media: "screen and (max-width: 600px)"
          title: "Small-screen Login"
        - cob://quux/mobile/login.css
    All five entries have an implicit or explicit "url" attribute,
    two have "media" attributes, and one has a "title".

    Different kinds of assets should derive specific classes with attributes
    from PathVal.
    """
    BaseAttrs = ('url',)
    Attrs = ()
    Directives = ()

    @classmethod
    def make(cls, url, **kwargs):
        assert isinstance(url, CobUrl)
        return cls(url=url, **kwargs)

    def __init__(self, **kwargs):
        # Never create a PathVal object directly; use cls.make()
        for key, value in kwargs.iteritems():
            assert key in (self.BaseAttrs + self.Attrs), (key, kwargs, self.__class__.__name__)
            setattr(self, key, value)

    def __repr__(self):
        return "<%s %s>" % (
            self.__class__.__name__,
            ", ".join("%s=%r" % (attr, getattr(self, attr))
                      for attr in (self.BaseAttrs + self.Attrs)
                      if hasattr(self, attr))
            )

    def __eq__(self, other):
        return all((hasattr(self, attr) == hasattr(other, attr)) and
                   (getattr(self, attr, None) == getattr(other, attr, None))
                   for attr in (self.BaseAttrs + self.Attrs))

    def serialize(self):
        d = dict((attr, getattr(self, attr)) for attr in self.Attrs if hasattr(self, attr))
        d['url'] = self.url.serialize()
        d['__class__'] = self.__class__.__name__
        return d

    # Note: _ClassMap must be explicitly computed in deserialize()
    # after all derived classes are defined.
    _ClassMap = None

    @classmethod
    def deserialize(cls, context, dct):
        if PathVal._ClassMap is None:
            PathVal._ClassMap = dict(
                (c.__name__, c) for c in itersubclasses(PathVal))
            PathVal._ClassMap['PathVal'] = PathVal

        kwargs = dct.copy()
        target_cls = PathVal._ClassMap[kwargs.pop('__class__')]
        url=CobUrl.deserialize(context, kwargs.pop('url'))
        return target_cls(url=url, **kwargs) # All other attrs should be a string

    @classmethod
    def is_directive_struct(cls, struct):
        for key in struct.__dict__.keys():
            if key in cls.Directives:
                return key
        return None

    @classmethod
    def make_from_entry(cls, entry, coburl, subdir):
        """Convert `entry` to a PathVal."""
        if isinstance(entry, basestring):
            pv = cls.make(coburl.join(subdir, entry))
#           import sys; print >>sys.stderr, pv
            return pv
        elif isinstance(entry, Struct):
            if hasattr(entry, 'url'):
                kwargs = entry.__dict__.copy()
    #           import sys; print >>sys.stderr, cls, type(entry), kwargs
                url = kwargs.pop('url')
                pv = cls.make(coburl.join(subdir, url), **kwargs)
    #           import sys; print >>sys.stderr, pv
                return pv
            else:
                directive = cls.is_directive_struct(entry)
                if directive:
#                   import sys; print >>sys.stderr, "Directive", cls, type(entry), entry
                    rv = Directive(entry)
#                   print >>sys.stderr, rv
                    return rv

        pass
#       import sys; print >>sys.stderr, cls, type(entry), entry
#       raise NotImplementedError("Can't handle attributes yet: %r" % entry)
        return None

    @property
    def is_simple(self):
        """A simple PathVal has only a `url` attribute."""
        return all(not hasattr(self, attr) for attr in self.Attrs)

    def template_dict(self, url):
        """Dictionary used in template loop"""
        return {
            'url': url,
        }

    @classmethod
    def find_pathvals(cls, coburl, path, *extensions, **kwargs):
        return [cls.make(c) for c in
                coburl.find_by_extensions(path, *extensions, **kwargs)]


class Directive(object):
    def __init__(self, struct):
        self.directive = struct

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.directive)

    def __eq__(self, other):
        return self.directive == other.directive


class GroupingPathVal(PathVal):
    Directives = ('^group')

class CssPathVal(GroupingPathVal):
    """An entry in the 'css' section of a node's config.

    `media` is the only supported attribute.

    Used by CssBundle.
    """
    Attrs = ('media',)
    Media = 'screen' # Hmm, should be 'all'

    def template_dict(self, url):
        media = getattr(self, 'media', self.Media)
        return self.make_template_dict(url, media)

    @classmethod
    def make_template_dict(cls, url, media=Media):
        return {
            'url':   url,
            'media': 'media="{0}"'.format(media) if media else '',
        }



class JsPathVal(GroupingPathVal):
    """An entry in the 'css' section of a node's config.

    `attrs` can be "defer", "async" or 'charset="UTF-8"'.

    Used by JavaScriptBundle.
    """
    Attrs = ('attrs',)

    def template_dict(self, url):
        return {
            'url':   url,
            'attrs': getattr(self, 'attrs', '')
        }


# Assets

class AssetName(object):
    """An asset's name, both in the build system (source)
    and the output (target)."""

    def __init__(self, source_pathval, target_url, mtime=0):
        self.source, self.target, self.mtime = source_pathval, target_url, mtime

    LocalTimeFormat = "%Y%m%dt%H%M%S"

    def __repr__(self):
        return "<%s source=%r, target=%r, mtime=%r>" % (
            self.__class__.__name__, self.source, self.target, self.timestamp())

    def __eq__(self, other):
        return (self.source == other.source
                and self.target == other.target
                and self.mtime == other.mtime)

    def timestamp(self):
        return None if self.mtime is None else format_seconds(
            self.mtime, self.LocalTimeFormat)

    def query_string(self):
        ts = self.timestamp()
        return ("?" + ts) if ts else ""

    def serialize(self):
        return dict(
            source=self.source.serialize(),
            target=self.target,
            mtime=self.mtime,
        )

    @classmethod
    def deserialize(cls, context, dct):
        return cls(PathVal.deserialize(context, dct['source']),
                   dct['target'],
                   dct['mtime'])



class TemplateTree(object):
    """
    A multilevel dict that will turn into a JavaScript object,
    where each "path" will lead to a Mustache template.
    """
    def __init__(self, **kwargs):
        self.tree = dict(**kwargs)

    def __repr__(self):
        return "<%s tree=%r>" % (self.__class__.__name__, self.tree)

    def add_leaf(self, branch_path, leaf, value):
        subtree = self.tree
        for p in branch_path:
            subtree = subtree.setdefault(p, {})
        assert leaf not in subtree
        subtree[leaf] = value

    def as_json(self, indent=4):
        return json.dumps(self.tree, indent=indent)


class HtmlTemplate(object):
    """Mustache HTML template"""
    def __init__(self, branch_path, coburl, data):
        self.branch_path, self.coburl, self.data = branch_path, coburl, data

    def __repr__(self):
        return "<%s branch_path=%r, coburl=%r, data=%r>" % (
            self.__class__.__name__, self.branch_path, self.coburl, self.data)

    def __eq__(self, other):
        return (self.branch_path == other.branch_path
                and self.coburl == other.coburl
                and self.data == other.data)

    def serialize(self):
        return dict(
            branch_path=self.branch_path,
            coburl=self.coburl.serialize(),
            data=self.data)

    @classmethod
    def deserialize(cls, context, dct):
        return cls(
            dct['branch_path'],
            CobUrl.deserialize(context, dct.get('coburl')),
            dct['data'])

    @classmethod
    def make_branch_path(cls, node_name):
        return node_name.split('.')

    @classmethod
    def load(cls, node_name, filepath, config):
        template_coburl = filepath.url
        try:
            data = read_file(template_coburl.abspath, cls_name=cls.__name__)
        except IOError:
            app.logger.exception(
                "Error reading %r; config=%r",
                template_coburl.abspath, config.coburl)
            raise
        return cls(cls.make_branch_path(node_name), template_coburl, data)

    def compute(self, profile, template_tree):
        template_tree.add_leaf(
            self.branch_path, shortname(self.coburl.path), self.data)

    @classmethod
    def make_template_tree(cls, **kwargs):
        return TemplateTree(**kwargs or {"view": {}, "page": {}, "html": {}})



class AssetSheaf(object):
    """A collection of assets, all of one kind; e.g., JavaScript or Images"""
    Extensions = None
    SubDir = None
    ConfigKey = None
    PathValClass = PathVal

    @classmethod
    def find_pathvals(cls, coburl, path, relative=False):
        return PathVal.find_pathvals(
            coburl, cls.path(path), *cls.Extensions, relative=relative)

    @classmethod
    def path(cls, path):
        return pathjoin(path, cls.SubDir)

    @classmethod
    def configured_pathvals(cls, coburl, config, config_key=None):
        """Find all pathvals associated with this class from config"""
        pathvals, config_key = [], config_key or cls.ConfigKey
        for entry in getattr(config.data, config_key, []):
            try:
                pv = cls.configure_pathval(coburl, entry)
                if pv:
                    pathvals.append(pv)
            except:
                app.logger.exception(
                    "Error reading %r from '%s', key='%s'",
                    entry, config.coburl, config_key)
                raise
        return pathvals

    @classmethod
    def configure_pathval(cls, coburl, entry):
        """Convert `entry` to a PathVal."""
        return cls.PathValClass.make_from_entry(entry, coburl, cls.SubDir)

    def compile(self, profile):
        raise NotImplementedError


class HtmlSheaf(AssetSheaf):
    """Mustache HTML templates in config files."""
    # TODO: use .mustache as file extension
    ConfigKey = SubDir = 'html'
    Extensions = ['.' + SubDir]

    def __init__(self, templates):
        self.templates = templates

    def __repr__(self):
        return "<%s templates=%r>" % (
            self.__class__.__name__,
            [t.coburl for t in self.templates])

    def __eq__(self, other):
        return self.templates == other.templates

    def serialize(self):
        return dict(templates=[t.serialize() for t in self.templates])

    @classmethod
    def deserialize(cls, context, dct):
        return cls([HtmlTemplate.deserialize(context, t)
                    for t in dct['templates']])

    @classmethod
    def load_sheaf(cls, node_name, coburl, path, config, config_key=None):
        templates = [HtmlTemplate.load(node_name, pv, config)
                     for pv in cls.configured_pathvals(
                             coburl, config, config_key)]
        return cls(templates)

    @property
    def pathvals(self):
        return [self.PathValClass.make(t.coburl) for t in self.templates]


class TemplateSheaf(HtmlSheaf):
    # Hmmm: why is this a list? Only makes sense as one element.
    ConfigKey = 'template'


class LangSheaf(AssetSheaf):
    """Localized strings in a set of _parallel_ config files."""
    # TODO: work with `Babel <http://babel.edgewall.org/>`__ and Flask-Assets
    SubDir = 'lang'
    Extensions = ['.json', '.yaml']

    def __init__(self, pathvals):
        self.pathvals = pathvals

    def __repr__(self):
        return "<%s pathvals=%r>" % (self.__class__.__name__, self.pathvals)

    def __eq__(self, other):
        return self.pathvals == other.pathvals

    def serialize(self):
        return dict(pathvals=[pv.serialize() for pv in self.pathvals])

    @classmethod
    def deserialize(cls, context, dct):
        return cls([PathVal.deserialize(context, pv) for pv in dct['pathvals']])

    @classmethod
    def load_sheaf(cls, node_name, coburl, path, config, config_key=None):
        return cls(cls.find_pathvals(coburl, path, relative=True))


class AssetBundle(webassets.Bundle, AssetSheaf):
    """A particular kind of webassets.Bundle for a node; e.g., JavaScript"""
    # TODO: actually build bundles
    ASSET_SEP = 70 * u'='
    Asset_Format = u"/* {0}\n * {1}\n */\n\n{2}\n"

    # TODO: handle compilation; e.g., Sass and CoffeeScript

    def __init__(self, pathvals):
        self.pathvals = []
        self.prepend(pathvals)

    def __repr__(self):
        return "<%s pathvals=%r>" % (self.__class__.__name__, self.pathvals)

    def __eq__(self, other):
        return self.pathvals == other.pathvals

    def serialize(self):
        return dict(pathvals=[pv.serialize() for pv in self.pathvals
                              if isinstance(pv, PathVal)])

    @classmethod
    def deserialize(cls, context, dct):
        return cls([PathVal.deserialize(context, pv) for pv in dct['pathvals']])

    def prepend(self, pathvals):
        self.pathvals = pathvals + self.pathvals
        self._update_pathvals(pathvals)

    def append(self, pathvals):
        self.pathvals = self.pathvals + pathvals
        self._update_pathvals(pathvals)

    def _update_pathvals(self, pathvals):
        contents = [pv.url.abspath for pv in pathvals
                    if isinstance(pv, PathVal)]
        # Yuck, re-init base class
        webassets.Bundle.__init__(self, *contents)

    @classmethod
    def load_sheaf(cls, node_name, coburl, path, config, config_key=None):
        pathvals = cls.configured_pathvals(coburl, config, config_key)
        if not pathvals and not config_key:
            pathvals = cls.find_pathvals(coburl, path, relative=True)
        return cls(pathvals)

    Ops = enum(Name=1, Combine=2, Copy=3, CombineTarget=4, Preamble=5)

    def compute_op_assets(self, node_coburl, reldir,
                          target_filename='', concatenate=None,
                          preamble=None, preamble_filename=None):
        """Compute a series of operations for all the assets"""
        # TODO: remove duplicate pathvals
        combiner_mtime, op_assets = 0, []

        def _hash_filename(hasher, fname):
            return pathjoin(reldir, hash_filename(hasher) + "_" + fname)

        if preamble:
            hasher = hashlib.sha256()
            hasher.update(preamble)
            op_assets.append(
                (self.Ops.Preamble,
                 AssetName(
                     None, _hash_filename(hasher, preamble_filename), None)))

        reset_combiner = True

        def emit_combination():
            if combiner_mtime > 0:
                op_assets.append(
                    (self.Ops.CombineTarget,
                     AssetName(None,
                               _hash_filename(hasher, target_filename),
                               None)))

        for pathval in self.pathvals:
            if reset_combiner:
                emit_combination()
                hasher = hashlib.sha256()
                combiner_mtime = 0
                reset_combiner = False

            if isinstance(pathval, Directive):
                reset_combiner = True
                continue

            coburl, op, mtime, target_url = pathval.url, None, None, None

            if coburl.is_local:
                mtime = modification_time(coburl.abspath)
                if mtime is None:
                    app.logger.warning("{0}: Can't read '{1}'".format(
                        node_coburl.path, coburl.path))
                    continue
                elif concatenate and pathval.is_simple:
                    combiner_mtime = max(combiner_mtime, mtime)
                    assert mtime > 0 and combiner_mtime > 0
                    op = self.Ops.Combine
                    target_url = None
                    hasher = hashfile(coburl.abspath, hasher)
                else:
                    op = self.Ops.Copy
                    if node_coburl.is_child_path(coburl):
                        target_url = pathjoin(
                            reldir,
                            self.target_filename(node_coburl.relpath(coburl)))
                    else:
                        target_url = coburl.path
            else:
                # remote asset
                op = self.Ops.Name
                target_url = coburl.path

            op_assets.append((op, AssetName(pathval, target_url, mtime)))

        # Emit final combination
        emit_combination()

#       app.logger.info("compute_op_assets: %r (reldir=%r)\n\t[%s]" % (
#           node_coburl.path, reldir, ',\n\t'.join(
#               "%s: %r" % (self.Ops.reverse_mapping[op], an)
#               for op, an in op_assets)))

        return op_assets

    def emit_assets(
            self, filecache, output_path, op_assets,
            preamble=None, use_symlink=False):
        combined_data, combined_filepath = [], None
        log = []
        for op, assetname in op_assets:
            source = assetname.source and assetname.source.url.abspath
            target = assetname.target and pathjoin(
                output_path, assetname.target)

            if op == self.Ops.Preamble:
                assert preamble is not None
                preamble_filepath = target
                write_file(preamble_filepath, preamble)
                log.append("Preamble %r" % preamble_filepath)
            elif op == self.Ops.CombineTarget:
                combined_filepath = target
                log.append("CombineTarget: %r" % combined_filepath)
                write_file(combined_filepath, '\f\n'.join(combined_data))
                combined_data, combined_filepath = [], None
            elif op == self.Ops.Combine:
                data = read_file(
                    source,
                    file_required=False,
                    cls_name=self.__class__.__name__)
                if data is None:
                    data = "/* Missing file */"
                    app.logger.warning("Can't read '{}'".format(source))
                combined_data.append(
                    self.Asset_Format.format(self.ASSET_SEP, source, data))
                log.append("Combine: %r" % assetname.source.url.path)
                # TODO: serve this file with a large Expiry time
            elif op == self.Ops.Copy:
                if use_symlink:
                    filecache.symlink(source, target)
                else:
                    filecache.copy(source, target)
                log.append("Copy: %r -> %r" % (
                    assetname.source.url.path, target))
            elif op == self.Ops.Name:
                log.append("Name: %r" % target)
        assert (not combined_data) == (not combined_filepath)
#       app.logger.info('\n'.join(log))

    @classmethod
    def target_filename(cls, filename):
        return filename

    @classmethod
    def template_dict(cls, url):
        """Dictionary used in template loop"""
        return {
            "url": url,
        }


class StaticBundle(AssetBundle):
    ConfigKey = SubDir = 'static'

    @classmethod
    def target_filename(cls, filename):
        # strip prefix
        prefix = cls.SubDir + "/"
        assert filename.startswith(prefix)
        return filename[len(prefix):]


class CssBundle(AssetBundle):
    # TODO: handle Sass, etc
    ConfigKey = SubDir = 'css'
    Extensions = ['.' + SubDir]
    PathValClass = CssPathVal

    @classmethod
    def template_dict(cls, url):
        """Dictionary used in template loop"""
        return CssPathVal.make_template_dict(url)


class ImageBundle(AssetBundle):
    ConfigKey = SubDir = 'img'
    Extensions = ['.png', '.jpg', '.jpeg', '.gif', '.cur', '.webp', '.bmp', '.ico']
    MimeTypes = {
        # Mime types for more obscure image types
        '.cur':  'image/x-icon',
        '.webp': 'image/webp',
    }


class JavaScriptBundle(AssetBundle):
    # TODO: handle CoffeeScript, etc
    ConfigKey = SubDir = 'js'
    Extensions = ['.' + SubDir]
    PathValClass = JsPathVal
