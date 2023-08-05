# -*- coding: utf-8 -*-

"""The Slingr Server"""

# TODO:
#   - rename this class to CobApp, as it's much more than a Server.
#   - hide `app` (the Flask application object);
#     expose it as `cob_app.flask_app`
#   - move `route` decorator into CobApp class.
#   - move some of the code in runtime.py into CobApp.

import argparse
import logging
import os
import datetime
import tempfile

from werkzeug.exceptions import NotFound
import flask

from slingr import (
    app, Build, CobRoot, ospath, Struct,
    process_page, cob_page, OsStatCache,
)

from eggsac.utils import timestamp

__all__ = (
    "route",
    "Server",
)


def route(rule, page_name, **options):
    """This decorator registers a Cob page controller for a URL rule.

    The controller must have the signature `page_controller(page)`

    :param rule: the URL rule as string
    :param page_name: the name of the page in the Cob config.
    :param options: As for :class:`~flask.app.route`, the options
                    to be forwarded to the underlying
                    :class:`~werkzeug.routing.Rule` object.
    """
    # Note: adapted from Flask.app.route decorator
    def decorator(page_controller):
        view_func = lambda **view_args: \
            process_page(app.root_dir, page_controller,
                         page_name, **view_args)
        # To make `url_for` work, view_func wrapper
        # must be "the same" as page_controller
        view_func.__name__ = page_controller.__name__
        view_func.__doc__ = page_controller.__doc__
        view_func.__dict__.update(page_controller.__dict__)

        # endpoint defaults to page_controller.__name__
        endpoint = options.pop('endpoint', None)
        app.add_url_rule(rule, endpoint, view_func, **options)

    return decorator


class Server(object):
    SERVER_NAME = '0.0.0.0'
    SERVER_PORT = 8080
    DEBUG = True
    OUTPUT = Build.Output
    SYMLINK = hasattr(os, 'symlink')  # Mac and Linux, not Windows
    CONCATENATE = False
    CDN_ROOT = ''
    BuildClass = Build
    DESCRIPTION = "Serve a Cob"

    @classmethod
    def make(cls, **kwargs):
        """Factory method.

        Returns server object and kwargs suitable for cls.serve().
        """
        root_dir = kwargs.pop('root_dir')  # required
        if root_dir is None:
            root_dir = os.getcwd()

        server = cls(root_dir=root_dir)
        server.host = kwargs.pop('host', cls.SERVER_NAME)
        server.port = kwargs.pop('port', cls.SERVER_PORT)
        server.debug = kwargs.pop('debug', cls.DEBUG)
        server.output = kwargs.pop('output', cls.OUTPUT)
        server.static_folder = kwargs.pop('static_folder', None)
        server.error_page = kwargs.pop('error_page', None)
        server.build_cls = kwargs.pop('build_cls', cls.BuildClass)
        server.concatenate = kwargs.pop('concatenate', cls.CONCATENATE)
        server.use_symlink = kwargs.pop(
            'use_symlink', server.debug and cls.SYMLINK
        ) and hasattr(os, 'symlink')
        server.cdn_root = kwargs.pop('cdn_root', cls.CDN_ROOT)
        server.run_server = kwargs.pop('run_server', False)
        server.save_state = kwargs.pop('save_state', not server.debug)
        server.use_reloader = kwargs.pop(
            'use_reloader', server.run_server and server.debug)

        return server, kwargs

    def __init__(self, root_dir):
        # Never create Server object directly; use cls.make()
        self.root_dir = os.path.realpath(os.path.expanduser(root_dir))

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.__dict__)

    def serve(
            self,
            compile_build=None,
            use_debugger=None,
            use_evalex=None,
            enable_profiler=None,
            profiler_dir=None,
            wsgi_app=None,
            threaded=True,
            **kwargs
        ):
        """Run a development server."""
        self.use_debugger = (
            self.debug if use_debugger is None else use_debugger)
        self.use_evalex = self.debug if use_evalex is None else use_evalex
        self.threaded = threaded
        if compile_build is None:
            compile_build = self.debug

        # If we're using the Werkzeug reloader,
        # parent and server processes differ;
        # otherwise, everything happens in the same process.
        assert (self.is_parent_process != self.is_server_process) \
            if self.use_reloader else \
            (self.is_parent_process and self.is_server_process)

        self.init_flask_app()
        self.do_build(compile_build)

        if self.run_server:
            self.set_wsgi_app(wsgi_app, enable_profiler, profiler_dir)
            self.run()

    def run(self, **kwargs):
        """Run the Flask app in dev-mode, which uses Werkzeug's `run_simple`

        By default, we run debug=True and use_reloader=True.
        """
        logging.getLogger('werkzeug').setLevel(logging.INFO)

        if self.is_server_process:
            self.start_router()
            self.build.watch_assets()

        app.run(self.host, self.port,
                debug=self.debug,
                extra_files=self.build.watched_files,
                use_reloader=self.use_reloader,
                use_debugger=self.use_debugger,
                use_evalex=self.use_evalex,
                threaded=self.threaded,
                **kwargs)

    def set_wsgi_app(self, wsgi_app, enable_profiler, profiler_dir):
        if wsgi_app:
            app.wsgi_app = wsgi_app(app.wsgi_app)

        if enable_profiler and profiler_dir is not None:
            print(" * Profiler enabled.  Output in '{0}'".format(profiler_dir))
            from werkzeug.contrib.profiler import ProfilerMiddleware

            app.wsgi_app = ProfilerMiddleware(
                app.wsgi_app, profile_dir=profiler_dir)

    @classmethod
    def is_werkzeug_child_process(cls):
        """Used as an optimization in dev-mode.

        The Werkzeug reloader spawns a child process which
        handles all requests. A thread in the child process
        watches all Python modules and `extra_files` (the Cob's
        build artifacts) to see if they have been modified
        since the child process started. If so,
        the child process exits. The parent process then
        spawns another child, which causes the latest Python
        modules to be loaded and our Cob to be rebuilt.

        Returns True if this is the child process.
        """
        # See werkzeug.serving.restart_with_reloader()
        return os.environ.get('WERKZEUG_RUN_MAIN') == 'true'

    @property
    def is_parent_process(self):
        return not self.use_reloader or not self.is_werkzeug_child_process()

    @property
    def is_server_process(self):
        return not self.use_reloader or self.is_werkzeug_child_process()

    @property
    def is_preload_phase(self):
        return self.use_reloader and not self.is_werkzeug_child_process()

    def init_flask_app(self):
        """Initialize properties on Flask's `app` before running Cob."""
        app.debug = self.debug
        app.root_dir = self.root_dir
        app.static_url_path = '/output'    # url name
        app.static_folder = self.static_folder or ospath.join(
            self.root_dir, self.output)  # physical location
        app.error_page = self.error_page
        return app

    def do_build(self, compile_build):
        """Either load a previously compiled build or compile a fresh one."""
        with OsStatCache():
            build_start = datetime.datetime.now()
            if self.is_server_process:
                print "\n{0}: Starting build".format(timestamp(build_start))

            build = self.make_build() if compile_build else self.load_build()
            app.build = self.build = build

            if self.is_server_process:
                print "{0}: Finished build in {1:.2f} seconds".format(
                    timestamp(),
                    (datetime.datetime.now() - build_start).total_seconds())

            return build

    def make_build(self):
        """Load and compile the Cob"""
        if self.is_preload_phase:
            # Speed up initialization: Do not waste time building the cob
            # before restarting under Werkzeug's run_simple reloader
            build = Struct({'watched_files': [], 'routes': {}})
        else:
            build = self.build_cls.make(
                CobRoot(self.root_dir), self.output)
            # compile and emit build
            build.run(
                concatenate=self.concatenate,
                use_symlink=self.use_symlink,
                cdn_root=self.cdn_root,
                save_state=self.save_state,
            )
        return build

    def load_build(self):
        """Load previously compiled Cob."""
        return self.build_cls.load(
            CobRoot(self.root_dir), self.output)

    def start_router(self):
        """Tell Flask about all page routes declared in cob.yaml."""
        for route, page_name in self.build.routes.iteritems():
            view_func = lambda page_name=page_name, **view_args: \
                process_page(app.root_dir, cob_page, page_name, **view_args)
            view_func.__name__ = str(page_name)
            app.add_url_rule(route, endpoint=page_name, view_func=view_func)

        # Handle /output/ requests.
        # In production, we configure Nginx (or some other webserver)
        # to handle /output/ directly.
        app.add_url_rule(app.static_url_path + '/<path:filename>',
                         endpoint='static',
                         view_func=self.send_output_file)

        # Static files in root of output tree from "static" section;
        # e.g., "/favicon.ico" or "/robots.txt"
        app.add_url_rule(
            '/<path:filename>',
            endpoint='root_static',
            view_func=self.send_output_file)

    def send_output_file(self, filename):
        """Handler for /output/ requests.

        Send files from FileCache source, if possible."""
        filename = self.build.filecache.get_filename(
            app.static_folder, filename)
        if not os.path.isfile(filename):
            raise NotFound()
        return flask.send_file(
            filename,
            conditional=True,
            cache_timeout=app.get_send_file_max_age(filename),
        )

    @classmethod
    def make_server(cls, **kwargs):
        """Parse command line, make Server object."""
        parser_args = cls.parse_args(**kwargs)
        # Command line overrides compile-time defaults in kwargs
        kwargs.update(parser_args.__dict__)
        return cls.make(**kwargs)  # server, kwargs

    @classmethod
    def parse_args(
            cls,
            caller__file__=None,
            root_dir=None,
            parser=None,
            description=None,
            host=None,
            port=None,
            debug=None,
            use_reloader=None,
            output=None,
            static_folder=None,
            compile_build=True,
            concatenate=None,
            use_symlink=None
    ):
        """Parse arguments for dev-mode server."""
        parser = parser or argparse.ArgumentParser(
            description=(description or cls.DESCRIPTION) + " (in dev-mode)",
        )

        if root_dir is None:
            if caller__file__:
                root_dir = os.path.dirname(caller__file__)
            else:
                root_dir = os.getcwd()
        root_dir = os.path.realpath(os.path.expanduser(root_dir))
        parser.add_argument(
            'root_dir',
            help='directory where Cob lives (default: "%(default)s")',
            default=os.path.abspath(root_dir), nargs='?')

        compile_load_group = parser.add_mutually_exclusive_group()
        compile_load_group.add_argument(
            '--compile', '-C', dest='compile_build', action='store_true',
            default=compile_build,
            help='Compile Build from scratch (default: %(default)s)')
        compile_load_group.add_argument(
            '--load', '-L', dest='compile_build', action='store_false',
            help='Load previously compiled Build')

        parser.add_argument(
            '--host',  '-t', default=host or cls.SERVER_NAME,
            help='Hostname to listen on (default: "%(default)s")')
        parser.add_argument(
            '--port',  '-p', default=port or cls.SERVER_PORT, type=int,
            help='Port of the webserver (default: %(default)s)')

        output = output or cls.OUTPUT
        parser.add_argument(
            '--output',  '-o', default=output,
            help='Output dir for Cob builder (default: "%(default)s")')
        static_folder = static_folder or os.path.join(root_dir, output)
        parser.add_argument(
            '--static-folder',  '-s', default=static_folder,
            help='Path to Flask static folder (default: "%(default)s")')

        concatenate_group = parser.add_mutually_exclusive_group()
        if concatenate is None:
            concatenate = cls.CONCATENATE
        concatenate_group.add_argument(
            '--concatenate',  '-j', default=concatenate, action='store_true',
            help='Concatenate JS and CSS files (default: %(default)s)')
        concatenate_group.add_argument(
            '--no-concatenate',  '-J',
            dest='concatenate', action='store_false',
            help='Emit individual JS and CSS files')

        debug_group = parser.add_mutually_exclusive_group()
        debug_group.add_argument(
            '--debug', '-d', default=debug or cls.DEBUG, action='store_true',
            help='enable Flask debugging (default: %(default)s)')
        debug_group.add_argument(
            '--no-debug', dest='debug', action='store_false',
            help='disable Flask debugging')

        reloader_group = parser.add_mutually_exclusive_group()
        reloader_group.add_argument(
            '--use-reloader', default=True, action='store_true',
            help='enable Werkzeug server process reloader '
                 '(default: %(default)s)')
        reloader_group.add_argument(
            '--no-use-reloader', dest='use_reloader', action='store_false',
            help='disable Werkzeug server process reloader')

        # Profiling using ProfilerMiddleware
        parser.add_argument(
            '--enable-profiler', action='store_true',
            help='enable profiling using ProfilerMiddleware')
        parser.add_argument(
            '--profiler-dir', default=tempfile.gettempdir(),
            help='Output directory for profiler (default: "%(default)s")')

        run_group = parser.add_mutually_exclusive_group()
        run_group.add_argument(
            '--run-server', default=True, action='store_true',
            help='Run server (default: %(default)s)')
        run_group.add_argument(
            '--no-run-server', dest='run_server', action='store_false',
            help="Don't run server; just compile")

        save_state_group = parser.add_mutually_exclusive_group()
        save_state_group.add_argument(
            '--save-state', default=False, action='store_true',
            help='Save state after compiling (default: %(default)s)')
        save_state_group.add_argument(
            '--no-save-state', dest='save_state', action='store_false',
            help="Don't save state after compiling")

        if hasattr(os, 'symlink'):
            symlink_group = parser.add_mutually_exclusive_group()
            if use_symlink is None:
                use_symlink = cls.SYMLINK
            symlink_group.add_argument(
                '--use-symlink', default=use_symlink, action='store_true',
                help='Symlink rather than copy files while building '
                     '(default: %(default)s)')
            symlink_group.add_argument(
                '--no-use-symlink', dest='use_symlink', action='store_false',
                help="Always copy files when building; don't symlink")

        return parser.parse_args()

    @classmethod
    def setup(cls, root_dir=None, **kwargs):
        """Used by setup_cob to compile the Cob to output."""
        server, _ = cls.make(
            root_dir=root_dir,
            debug=False,
            concatenate=True,
            use_symlink=False,
            save_state=True,
            **kwargs
        )

        server.do_build(compile_build=True)
        return server

    @classmethod
    def wsgi(cls, root_dir=None, logdir=None, **kwargs):
        """Bootstrap the Slingr (Flask) app for WSGI Gateway"""
        server, kwargs = cls.make(
            root_dir=root_dir, debug=False, **kwargs)
        server.init_flask_app()
        server.do_build(compile_build=False)  # load previously compiled build
        server.start_router()

        # FIXME
        logdir = logdir or '/var/tmp'
        hdlr = logging.FileHandler(os.path.join(logdir, 'myapp.log'))
        app.logger.addHandler(hdlr)
        app.logger.setLevel(logging.DEBUG)
        return app
