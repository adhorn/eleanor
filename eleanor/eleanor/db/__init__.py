from flask_sqlalchemy import SQLAlchemy, get_state
import sqlalchemy.orm as orm
from functools import partial
from flask import current_app
# import traceback
# import sys
import os


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

        # Everything else goes to the slave
        else:
            if os.environ.get('MASTER') == 'FORCE':
                current_app.logger.debug("Forcing -> MASTER")
                return state.db.get_engine(self.app, bind='master')
            else:
                current_app.logger.debug("Connecting -> SLAVE")
                return state.db.get_engine(self.app, bind='slave')

        # else:
        #     current_app.logger.debug("Connecting -> SLAVE")
        #     try:
        #         st = state.db.get_engine(self.app, bind='slave')
        #     except Exception:
        #         traceback.print_exc()
        #         e = sys.exc_info()[0]
        #         current_app.logger.debug(
        #             "cant use SLAVE. trying MASTER again:" + e)
        #         st = state.db.get_engine(self.app, bind='master')
        #     return st

    _name = None

    def using_bind(self, name):
        s = RoutingSession(self.db)
        vars(s).update(vars(self))
        s._name = name
        return s

        # db.session.using_bind("master").query(
        #     FooModel).filter(FooModel.id == id).update(
        #     {
        #         FooModel.count: FooModel.count + 1,
        #         FooModel.updated: _foobar_timestamp
        #     }
        # )


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
