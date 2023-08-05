# -*- coding: utf-8 -*-
"""
Build an application
"""

from __future__ import absolute_import

from slingr import app
from slingr.common import (
    format_seconds, modification_time, Struct, YamlConfigReaderWriter)
from slingr.coburl import CobUrl, pathjoin


# Config

class _Config(object):
    ConfigReaderWriterClass = YamlConfigReaderWriter

    def __init__(self, data, coburl=None, mtime=0):
        self.data = Struct(data)
        self.coburl = coburl
        self.mtime = mtime

    def __repr__(self):
        return "<%s coburl=%r, mtime=%s, data=%r>" % (
            self.__class__.__name__,
            self.coburl,
            format_seconds(self.mtime),
            self.data)

    def __eq__(self, other):
        return self.data == other.data and self.coburl == other.coburl

    def serialize(self):
        dct = dict(data=self.data.as_dict())
        if self.coburl:
            dct['coburl'] = self.coburl.serialize()
        return dct

    @classmethod
    def deserialize(cls, context, dct):
        return cls(
            dct['data'], CobUrl.deserialize(context, dct.get('coburl')))

    @classmethod
    def load(
            cls, parent_coburl, path, filename=None,
            reader_cls=None, file_required=True):
        filename = filename or cls.FileName
        reader_cls = reader_cls or cls.ConfigReaderWriterClass
        filepath = pathjoin(path, filename + reader_cls.Extension)
        coburl = parent_coburl.make(filepath)

        try:
            data = reader_cls.read_config_file(coburl.abspath)
        except IOError:
            # Note: not handling ParserErrors here
            if file_required:
                app.logger.warning(
                    "Couldn't read %s('%s')", cls.__name__, filepath)
                raise
            else:
                return None

        coburl.watch_file()
        mtime = modification_time(coburl.abspath)
#       app.logger.info("Loaded {}('{}')".format(cls.__name__, filepath))
        return cls(data, coburl, mtime)


class GlobalConfig(_Config):
    """Top-level global config"""
    FileName = 'global'


class ProfilesConfig(_Config):
    """Top-level profiles config"""
    FileName = 'profiles'


class NodeConfig(_Config):
    """Config for a node (page, view, page-view), etc"""
    FileName = 'config'
