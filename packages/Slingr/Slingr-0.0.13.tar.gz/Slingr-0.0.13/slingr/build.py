# -*- coding: utf-8 -*-
"""
Build an application
"""

from __future__ import absolute_import

import logging
import datetime
import shutil
import threading

from slingr import __version__
from slingr.common import (
    OutputFileCache, LocalTimeFormat,
    make_clean_dir, makedirs, Struct,
    JsonConfigReaderWriter, ospath)
from slingr.coburl import CobUrl
from slingr.node import Node, GlobalNode, Page
from slingr.watch import PathValMapWatcher


# CobState

class CobState(object):
    """Serializable state of a Cob application.

    Pages are compiled into CobState,
    which can be saved to disk during setup
    and loaded during app initialization on production."""
    ConfigReaderWriterClass = JsonConfigReaderWriter

    def __init__(self, coburl, global_node, profiles,
                 page_names, routes, pages):
        self.coburl, self.global_node, self.profiles = \
            coburl, global_node, profiles
        self.page_names, self.routes, self.pages = \
            page_names, routes, pages

    def __repr__(self):
        return "<%s coburl=%r, global_node=%r, profiles=%r, pages=%r>" % (
            self.__class__.__name__,
            self.coburl,
            self.global_node,
            self.profiles,
            self.pages)

    def __eq__(self, other):
        return (self.coburl == other.coburl
                and self.global_node == other.global_node
                and self.profiles == other.profiles
                and self.pages == other.pages)

    def serialize(self):
        return {
            "_metadata": {
                "date": datetime.datetime.now().strftime(LocalTimeFormat),
                "version": __version__
            },
            "global_node": self.global_node.serialize(),
            "profiles": self.profiles,
            "page_names": self.page_names,
            "routes": self.routes,
            "pages": self.serialize_pages(self.pages),
        }

    @classmethod
    def deserialize(cls, context, dct):
        global_node = GlobalNode.deserialize(context, dct['global_node'])
        pages = cls.deserialize_pages(context, dct['pages'])
        return cls(
            CobUrl(context.cobroot, ''),
            global_node,
            dct['profiles'],
            dct['page_names'],
            dct['routes'],
            pages)

    @classmethod
    def serialize_pages(cls, pages):
        return {
            page_name: {
                profile_name: page_profile.serialize()
                for profile_name, page_profile in page_profiles.iteritems()
            } for page_name, page_profiles in pages.iteritems()
        }

    @classmethod
    def deserialize_pages(cls, context, dct):
        return {
            page_name: {
                profile_name: Page.deserialize(context, page_profile)
                for profile_name, page_profile in page_profiles.iteritems()
            } for page_name, page_profiles in dct.iteritems()
        }

    def save(self, file_path):
        return self.ConfigReaderWriterClass.write_config_file(
            self.serialize(), file_path)

    @classmethod
    def load(cls, context, file_path):
        return cls.deserialize(
            context, cls.ConfigReaderWriterClass.read_config_file(file_path))


# PageValidators

class PageValidator(object):
    """Watch PathVals associated with each page_profile for updates.

    Used in dev-mode to detect if assets have been modified."""
    def __init__(self):
        self._lock = threading.RLock()
        self.watcher = PathValMapWatcher()

    def __repr__(self):
        return "<%s>" % (
            self.__class__.__name__,
        )

    def register(self, key, pathvals, invalidate):
        self.watcher.register(
            key,
            pathvals,
            lambda k, c, n: self.coburl_watcher_notify(
                invalidate, k, c, n))

    def coburl_watcher_notify(self, invalidate, key, coburl, now):
        with self._lock:
            invalidate(key, coburl, now)

    def watch(self):
        self.watcher.watch()

    def revalidate_page(self, page_profile, recompiler):
        with self._lock:
            if page_profile.invalidation:
                page_profile = recompiler(page_profile)
            return page_profile


class ReadOnlyPageValidator(object):
    """Dummy PageValidator used in production runs."""
    def revalidate_page(self, page_profile, recompiler):
        """No-op: page is always valid in production."""
        return page_profile

    def register(self, *args):
        pass

    def watch(self, *args):
        pass


# Build

class Build(object):
    Output = 'output'
    StateFile = 'web'
    DefaultOptions = {
        "save_state": True,
        "minify": True,
        "concatenate": True,
    }

    @classmethod
    def clear_caches(cls):
        Node.clear_cache()

    @classmethod
    def make(cls, cobroot, output=Output):
        """Factory method: loads from config files"""
        cls.clear_caches()
        coburl = CobUrl(cobroot, CobUrl.RootPath)
        global_node = GlobalNode.load_with_config(coburl)
        profiles = cls.load_profiles(global_node)
        page_names, routes = cls.load_page_names(global_node)
        cobstate = CobState(
            coburl, global_node, profiles, page_names, routes, {})
        page_validator = PageValidator()
        return cls(output, cobstate, page_validator)

    @classmethod
    def load(cls, cobroot, path=None, filename=StateFile):
        """Load previously compiled state."""
        cls.clear_caches()
        context = Struct({"cobroot": cobroot})
        file_path = cobroot.join(path, filename)
        cobstate = CobState.load(context, file_path)
        page_validator = ReadOnlyPageValidator()
        return cls(path, cobstate, page_validator)

    def save_cobstate(self, filename=StateFile):
        self.cobstate.save(ospath.join(self.output_path, filename))

    def __init__(self, output, cobstate, page_validator):
        self.output, self.cobstate, self.page_validator = (
            output, cobstate, page_validator)
        self.output_path = self.cobstate.coburl.join(self.output).abspath
        self.filecache = OutputFileCache(self.output_path, save_state=True)

    def __repr__(self):
        return ("<%s coburl=%r, profiles=%r, pages=%r, "
                "views=%r, page_validator=%r>") % (
            self.__class__.__name__,
            self.cobstate.coburl,
            self.cobstate.profiles,
            self.cobstate.page_names,
            self.cobstate.global_node.views.names(),
            self.page_validator
        )

    @classmethod
    def load_profiles(cls, global_node):
        return global_node.config.data.profiles

    @classmethod
    def load_page_names(cls, global_node):
        return cls.parse_page_declarations(
            getattr(global_node.config.data, 'pages', []))

    @classmethod
    def parse_page_declarations(cls, pages):
        page_names, routes = [], {}
        for page in pages:
            if isinstance(page, basestring):
                name = page
            else:
                name = page.page
                if hasattr(page, 'route'):
                    routes[page.route] = name
            page_names.append(name)
        return page_names, routes

    @property
    def routes(self):
        return self.cobstate.routes

    def compile(self, options):
        """Compile application in memory"""
        self.compiled_global_node = self.compile_global_node(options)
        pages = {}
        for page_name in self.cobstate.page_names:
            pages[page_name] = self.compile_page(page_name, options)
        self.cobstate.pages = pages
        return pages

    def compile_global_node(self, options):
        gn = self.cobstate.global_node
        gn.compute_html_templates()
        gn.compile(gn, options)

    def compile_page(self, page_name, options):
        page = {}
        try:
            for profile in self.cobstate.profiles:
                page[profile] = self.compile_page_profile(
                    page_name, profile, options)
        except IOError:
            logging.exception("Can't load page '%s'", page_name)
            raise  ## TODO: abort early option?
        return page

    def revalidate_page(self, page_profile):
        return self.page_validator.revalidate_page(
            page_profile, recompiler=self.recompile_page_profile)

    def recompile_page_profile(self, page_profile):
        self.clear_caches()
        page_name, profile_name = (
            page_profile.page_name, page_profile.profile)
        pp = self.compile_page_profile(page_name, profile_name, self.options)
        self.cobstate.pages[page_name][profile_name] = pp
        pp.index_page = self.emit_page_profile(pp, self.options)
        print("Recompiled: %r" % pp)
        return pp

    def compile_page_profile(self, page_name, profile_name, options):
        pp = Page.make_profile(self.cobstate.coburl, page_name, profile_name)
        pp.compile(self.cobstate.global_node, options)
        return pp

    def clean_output(self, output_path=None):
        make_clean_dir(output_path or self.output_path)

    def emit(self, options):
        """Write compiled application to output directory"""
        self.clean_output()
        self.cobstate.global_node.compiled.emit(
            self.filecache, self.output_path, self.output, '', options)
        for page in self.cobstate.pages.values():
            for page_profile in page.values():
                page_profile.index_page = self.emit_page_profile(
                    page_profile, options)

    def emit_page_profile(self, page_profile, options):
        reldir = page_profile.output_dir()
        target_dir = ospath.join(self.output_path, reldir)
        shutil.rmtree(target_dir, ignore_errors=True)
        makedirs(target_dir)
        return page_profile.compiled.emit(
            self.filecache, self.output_path, self.output, reldir, options)

    def set_options(self, **kwargs):
        self.options = dict(self.DefaultOptions)
        self.options.update(**kwargs)
        # Avoid writing FileCache to disk, if requested
        self.filecache.save_state = self.options['save_state']

    def run(self, **kwargs):
        self.set_options(**kwargs)
        self.compile(self.options)
        self.emit(self.options)
        if self.options['save_state']:
            self.save_cobstate()

    def watch_assets(self):
        for page_name, page_profiles in self.cobstate.pages.iteritems():
            for profile_name, page_profile in page_profiles.iteritems():
                self.page_validator.register(
                    (page_name, profile_name),
                    page_profile.pathvals,
                    self.invalidate_page
                )
        self.page_validator.watch()

    def invalidate_page(self, key, coburl, now):
        (page_name, profile_name) = key
        page_profile = self.cobstate.pages[page_name][profile_name]
        page_profile.invalidate(now)
        print "%s: Invalidated: coburl=%r, page_profile=%r" % (
            now.strftime(LocalTimeFormat), coburl, page_profile)

    def clone_tree(self, use_symlink, *path):
        src = self.cobstate.coburl.join(*path).abspath
        dst = ospath.join(self.output_path, *path)
        self.filecache.clone_tree(src, dst, use_symlink)

    @property
    def watched_files(self):
        return self.cobstate.coburl.watched_files
