# -*- coding: utf-8 -*-

"""
Setup helpers for Cobs.
"""

from __future__ import absolute_import

from setuptools import setup as setuptools_setup
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from setuptools.command.sdist import sdist as _sdist

import os, fnmatch, glob, shutil, sys


def recursive_data_files(treeroot, patterns=['*']):
    """Return sequence of files in format expected by Distutil's data_files:
    a sequence of (target_dir, [f1, ..., fN]) pairs."""
    results = []
    for base, dirs, files in os.walk(treeroot):
        for pattern in patterns:
            goodfiles = fnmatch.filter(files, pattern)
            if goodfiles:
                results.append(
                    (base, [os.path.join(base, f) for f in goodfiles]))
    return results

def make_data_files(output='output'):
    data_files = (
        [('', ['cob.yaml'])]
        + recursive_data_files(output)
    )
    return data_files

def make_filelist(output='output'):
    # Flatten make_data_files() result into a simple list
    return [f for path, files in make_data_files(output) for f in files]

build_cob_params = {} # Hack

def build_cob(root_dir=None):
    import slingr.server

    # Ugh. Can't figure out how to pass build_cob_params in bdist_egg and sdist
    root_dir = root_dir or os.path.abspath(".")
    server_cls = build_cob_params.pop('server_cls', slingr.server.Server)
    server = server_cls.setup(root_dir=root_dir, **build_cob_params)
#   print("build_cob: server", server)
    return server

class bdist_egg(_bdist_egg):
    def initialize_options(self):
#       print "bdist_egg.initialize_options"
        build_cob()
        self.distribution.data_files += make_data_files()
        _bdist_egg.initialize_options(self)

class sdist(_sdist):
    def check_readme(self):
        # Ugh. No official extension point in setuptools.command.sdist
        # to modify filelist
#       print "sdist.check_readme"
        build_cob()
        self.filelist.extend(make_filelist())

        # Modern packages have reStructuredText or Markdown READMEs
        for readme in ("README.rst", "README.md"):
            if os.path.exists(readme):
                self.filelist.append(readme)
                break
        else:
            _sdist.check_readme(self)

def cleanup_globs(root, pattern):
    for f in glob.glob(os.path.join(os.path.abspath(root), pattern)):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)

def cleanup_slingr_bootstrap(root='.'):
    cleanup_globs(root, '*.egg')

def build_setup_options_from_cob_ini(setup_options, cfg, package_dir):
    if cfg.has_section('setup'):
        for opt in cfg.options('setup'):
            value = cfg.get('setup', opt)
            if opt == 'package_name':
                setup_options['name'] = value
            elif opt == 'readme':
                setup_options['long_description'] = open(
                    os.path.join(package_dir, value)).read()
            else:
                setup_options[opt] = value
    return setup_options

def setup(setup_py_filename, **options):
    import eggsac.utils
    import slingr.eggsac_config

    package_dir = os.path.dirname(os.path.abspath(setup_py_filename))
    cfg = eggsac.utils.read_ini(
        package_dir, slingr.eggsac_config.INI_FILENAME)

    setup_options = dict(
        cmdclass={
            'bdist_egg': bdist_egg,
            'sdist':     sdist,
        },
        install_requires=[
            'Slingr',
        ],
        zip_safe=False,
    )

    # Ugh. Can't figure out how to set this in bdist_egg and sdist
    build_cob_params.update(options.pop('build_cob_params', {}))
    sys.stderr.write("Setting build_cob_params=%r\n" % build_cob_params)

    setup_options = build_setup_options_from_cob_ini(
        setup_options, cfg, package_dir)
    setup_options.update(options)

    # Let setuptools do all the heavy lifting
    setuptools_setup(**setup_options)
    cleanup_slingr_bootstrap(package_dir)
