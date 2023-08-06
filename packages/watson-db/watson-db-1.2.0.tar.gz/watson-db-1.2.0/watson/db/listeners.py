# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from watson.di import ContainerAware
from watson.framework import events


class Init(ContainerAware):

    """Bootstraps watson.db into the event system of watson.

    Each session and engine can be retrieved from the container by using
    sqlalchemy_engine_[name of engine] and sqlalchemy_session_[name of session]
    respectively.
    """

    def __call__(self, event):
        app = event.target
        if 'db' not in app.config:
            raise ValueError(
                'No db has been configured in your application configuration.')
        if 'sqlalchemy_declarative_base' not in app.config['dependencies']['definitions']:
            self.container.add('sqlalchemy_declarative_base', declarative_base(name='Model'))
        for session, config in app.config['db'].items():
            # Configure the engine options and add it to the container
            engine = 'sqlalchemy_engine_{0}'.format(session)
            engine_init_args = config.get('engine_options', {})
            engine_init_args['name_or_url'] = config['connection_string']
            self.container.add_definition(
                engine,
                {
                    'item': 'watson.db.engine.make_engine',
                    'init': engine_init_args
                })
            # Configure the session options and add it to the container
            session_init_args = config.get('session_options', {})
            session_init_args['bind'] = engine
            self.container.add_definition(
                'sqlalchemy_session_{0}'.format(session),
                {
                    'item': 'watson.db.session.Session',
                    'init': session_init_args
                })
        if ('watson.db.listeners.Complete',) not in app.config['events'].get(events.COMPLETE, {}):
            app.dispatcher.add(
                events.COMPLETE,
                self.container.get('watson.db.listeners.Complete'),
                1,
                False)


class Complete(ContainerAware):

    """Cleanups the db session at the end of each request.
    """

    def __call__(self, event):
        app = event.target
        if 'db' not in app.config:
            raise ValueError(
                'No db has been configured in your application configuration.')  # pragma: no cover
        for session, config in app.config['db'].items():
            session_name = 'sqlalchemy_session_{0}'.format(session)
            session = self.container.get(session_name)
            session.close()
