from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from logging import getLogger
import os
from sqlalchemy.schema import CreateTable
_logger = getLogger('poff')

db = SQLAlchemy()

def create_app(config_file=None):
    _init_logging()

    app = Flask('poff')
    if config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar('POFF_CONFIG_FILE')

    db.init_app(app)

    from . import views

    app.register_blueprint(views.mod)

    @app.teardown_appcontext
    def teardown_appcontext(error):
        """ Commits the session if no error has occured, otherwise rollbacks. """
        if error is None:
            try:
                db.session.commit()
            except Exception: # pylint: disable=broad-except
                # Whoopsie! We can't
                db.session.rollback()
                _logger.exception('Exception modened during teardown commit.')
        else:
            # We have an exception, but it has probably already been handled by the modroriate handlers,
            # so just rollback the session and ignore the error
            db.session.rollback()
        db.session.remove()


    return app


def _init_logging():
    import logging
    logging.basicConfig(format='%(asctime)s %(levelname)-10s %(name)s %(message)s', level=logging.DEBUG)


def cli_entry():
    """ CLI entrypoint. Start the server. """
    import argparse
    parser = argparse.ArgumentParser(prog='poff')
    parser.add_argument('-b', '--host',
        metavar='<host>',
        default='127.0.0.1',
        help='Which address to listen to. Default: %(default)s',
    )
    parser.add_argument('-p', '--port',
        metavar='<port>',
        type=int,
        default=5353,
        help='Which port to bind to. Default: %(default)s',
    )
    parser.add_argument('-c', '--config-file',
        metavar='<config-file>',
        help='Config file to use. If none is given, will load from the envvar POFF_CONFIG_FILE.',
    )
    parser.add_argument('-d', '--debug',
        action='store_true',
        default=False,
        help='Show debug inforamtion on errors. DO NOT RUN WITH THIS OPTION IN PRODUCTION!',
    )

    subparser = parser.add_subparsers(title='action',
        help='Action to be performed',
    )

    serve_parser = subparser.add_parser('serve',
        help='Run the webserver',
    )
    serve_parser.set_defaults(target=serve)

    init_parser = subparser.add_parser('init',
        help='Create the database tables',
    )
    init_parser.set_defaults(target=_init_db)
    args = parser.parse_args()
    args.target(args)


def serve(args):
    """ Run the webserver. """
    app = create_app(config_file=args.config_file)
    app.run(host=args.host, port=args.port, debug=args.debug)


def _init_db(args):
    """ Initialize the database tables. """
    app = create_app(config_file=args.config_file)
    config_location = args.config_file or os.environ['POFF_CONFIG_FILE']
    _logger.info('Using config at %s', config_location)
    #from poff import models
    with app.app_context():
        print(''.join([str(CreateTable(table).compile(db.engine)) for table in db.get_tables_for_bind()]))
        _logger.info('Initializing tables...')
        db.create_all()
    _logger.info('Tables initialized.')
