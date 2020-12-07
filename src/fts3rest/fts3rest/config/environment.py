#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
#
#   See www.eu-emi.eu for details on the copyright holders
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Pylons environment configuration"""
import os
import pylons

from distutils.version import StrictVersion
is_pylons_0 = '(not installed)' != pylons.__version__ and (StrictVersion(pylons.__version__) < StrictVersion('1.0'))

if is_pylons_0:
    from pylons import config as pylons_config
else:
    from pylons.configuration import PylonsConfig

from mako.lookup import TemplateLookup
from sqlalchemy import engine_from_config, event

import fts3rest.lib.app_globals as app_globals
import fts3rest.lib.helpers
from fts3.util.config import fts3_config_load
from fts3rest.lib.helpers.connection_validator import connection_validator, connection_set_sqlmode
from fts3rest.config.routing import make_map
from fts3rest.model import init_model

import logging
log = logging.getLogger(__name__)

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    log.debug('entered load_environment')
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    if is_pylons_0:
        config = pylons_config
    else:
        config = PylonsConfig()
    config.init_app(global_conf, app_conf, package='fts3rest', paths=paths)

    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = fts3rest.lib.helpers

    # Setup cache object as early as possible
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)

    # If fts3.config is set, load configuration from there
    fts3_config_file = config.get('fts3.config')
    if fts3_config_file:
        log.debug('call fts3_config_load')
        fts3cfg = fts3_config_load(fts3_config_file)
        # Let the database be overriden by fts3rest.ini
        if 'sqlalchemy.url' in config and 'sqlalchemy.url' in fts3cfg:
            del fts3cfg['sqlalchemy.url']
        config.update(fts3cfg)

    # Setup the SQLAlchemy database engine
    kwargs = dict()
    if config['sqlalchemy.url'].startswith('mysql://'):
        import MySQLdb.cursors
        kwargs['connect_args'] = {'cursorclass': MySQLdb.cursors.SSCursor}
    engine = engine_from_config(config, 'sqlalchemy.', pool_recycle=7200, **kwargs)
    init_model(engine)

    # Disable for sqlite the isolation level to work around issues with savepoints
    if config['sqlalchemy.url'].startswith('sqlite'):
        @event.listens_for(engine, "connect")
        def do_connect(dbapi_connection, connection_record):
            dbapi_connection.isolation_level = None

    # Catch dead connections
    event.listens_for(engine, 'checkout')(connection_validator)
    event.listens_for(engine, 'connect')(connection_set_sqlmode)

    # Mako templating
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
    )

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    return config
