#!/Users/georger/.virtualenvs/todo_deploy/bin/python

"""Scripts for Slingr"""

import os.path
from flask.ext.script import Manager, Server, Shell, Option

import slingr.build
import slingr.server

# configure your app
from slingr import app

def _make_context():
    return dict(app=app)

manager = Manager(app)


@manager.command
def build(root):
    "Build a Cob"
    root = os.path.abspath(root)
    build = slingr.server.make_build(root, slingr.server.OUTPUT)


class SlingrServer(Server):
    def __init__(self, root='.', output=slingr.server.OUTPUT,
                 *args, **kwargs):
        self.root = root
        self.output = output
        kwargs['port'] = kwargs.pop('port', slingr.server.SERVER_PORT)
        super(SlingrServer, self).__init__(*args, **kwargs)

    def get_options(self):
        options = (
            Option('-R', '--root',
                   default=self.root),
            Option('-o', '--output',
                   default=self.output),
        )
        return options + super(SlingrServer, self).get_options()

    def handle(self, app, root, host, port, output, **kwargs):
        options = dict(self.server_options)
        options.update(kwargs)
        slingr.server.serve(
            root_dir=root,
            host=host,
            port=port,
            output=output,
            debug= options['use_debugger'],
            **options)

manager.add_command(
    "runserver",
    SlingrServer(
        host=slingr.server.SERVER_NAME,
        port=slingr.server.SERVER_PORT))

manager.add_command(
    "shell",
    Shell(make_context=_make_context))

def sling():
    """ Entry point for console_scripts, so that you can
        'sling serve <path>', etc.
    """
    manager.run()


if __name__ == "__main__":
    sling()
