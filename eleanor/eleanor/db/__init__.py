from flask_sqlalchemy import SQLAlchemy, get_state
import sqlalchemy.orm as orm
from functools import partial
from flask import current_app
from eleanor.utils.redis import get_key


class RoutingSession(orm.Session):

    def __init__(self, db, autocommit=False, autoflush=False, **options):
        self.app = db.get_app()
        self.db = db
        self._model_changes = {}
        orm.Session.__init__(
            self, autocommit=autocommit, autoflush=autoflush,
            bind=db.engine,
            binds=db.get_binds(self.app), **options)

    def get_bind(self, mapper=None, clause=None):

        try:
            state = get_state(self.app)
        except (AssertionError, AttributeError, TypeError) as err:
            current_app.logger.debug(
                "cant get configuration. default bind. Error:" + err)
            return orm.Session.get_bind(self, mapper, clause)

        """
        If there are no binds configured, connect using the default
        SQLALCHEMY_DATABASE_URI
        """
        if state is None or not self.app.config['SQLALCHEMY_BINDS']:
            if not self.app.debug:
                current_app.logger.debug("Connecting -> DEFAULT")
            return orm.Session.get_bind(self, mapper, clause)

        elif self._name:
            self.app.logger.debug("Connecting -> {}".format(self._name))
            return state.db.get_engine(self.app, bind=self._name)

        # Writes go to the master
        elif self._flushing:  # we who are about to write, salute you
            current_app.logger.debug("Connecting -> MASTER")
            return state.db.get_engine(self.app, bind='master')

            '''
            Reads go to the slave if slave is up
            or default to master is the slave is down
            '''
        else:
            '''
            after a failed healthcheck of the slave
            env[MASTER] set to FORCE
            if healthcheck of the slave is success, env[MASTER] set to NO
            more info - see echo_api.py
            '''
            current_app.logger.debug("CACHE MASTER ==== {} ".format(get_key('MASTER')))
            if get_key('MASTER') == b'FORCE':
                current_app.logger.debug("Forcing -> MASTER")
                return state.db.get_engine(self.app, bind='master')
            else:
                current_app.logger.debug("Connecting -> SLAVE")
                return state.db.get_engine(self.app, bind='slave')

            # try:
            #     current_app.logger.info("Connecting -> SLAVE")
            #     raise
            #     return state.db.get_engine(self.app, bind='slave')
            # except Exception:
            #     current_app.logger.info("Falling back -> MASTER")
            #     return state.db.get_engine(self.app, bind='master')

    _name = None

    def using_bind(self, name):
        s = RoutingSession(self.db)
        vars(s).update(vars(self))
        s._name = name
        return s

        # usage: db.session.using_bind("master").query(ProductModel).all()


class RouteSQLAlchemy(SQLAlchemy):

    def __init__(self, *args, **kwargs):
        SQLAlchemy.__init__(self, *args, **kwargs)
        self.session.using_bind = lambda s: self.session().using_bind(s)

    def create_scoped_session(self, options=None):
        if options is None:
            options = {}
        scopefunc = options.pop('scopefunc', None)
        return orm.scoped_session(
            partial(RoutingSession, self, **options), scopefunc=scopefunc
        )


db = RouteSQLAlchemy()
