import os

import terminado
from ..utils import check_version

if not check_version(terminado.__version__, '0.8.3'):
    raise ImportError("terminado >= 0.8.3 required, found %s" % terminado.__version__)

from ipython_genutils.py3compat import which
from notebook.utils import url_path_join as ujoin
from .terminalmanager import TerminalManager
from .handlers import TerminalHandler, TermSocket
from . import api_handlers


def initialize(nb_app):
    if os.name == 'nt':
        default_shell = 'powershell.exe'
    else:
        default_shell = which('sh')
    shell = nb_app.terminado_settings.get('shell_command',
                                          [os.environ.get('SHELL') or default_shell]
                                          )
    # Enable login mode - to automatically source the /etc/profile script
    if os.name != 'nt':
        shell.append('-l')
    terminal_manager = nb_app.web_app.settings['terminal_manager'] = TerminalManager(
        shell_command=shell,
        extra_env={'JUPYTER_SERVER_ROOT': nb_app.notebook_dir,
                   'JUPYTER_SERVER_URL': nb_app.connection_url,
                   },
        parent=nb_app,
    )
    terminal_manager.log = nb_app.log
    base_url = nb_app.web_app.settings['base_url']
    handlers = [
        (ujoin(base_url, r"/terminals/(\w+)"), TerminalHandler),
        (ujoin(base_url, r"/terminals/websocket/(\w+)"), TermSocket,
             {'term_manager': terminal_manager}),
        (ujoin(base_url, r"/api/terminals"), api_handlers.TerminalRootHandler),
        (ujoin(base_url, r"/api/terminals/(\w+)"), api_handlers.TerminalHandler),
    ]
    nb_app.web_app.add_handlers(".*$", handlers)
