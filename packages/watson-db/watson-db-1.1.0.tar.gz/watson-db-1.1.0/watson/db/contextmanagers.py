# -*- coding: utf-8 -*-
from contextlib import contextmanager


@contextmanager
def transaction_scope(session):
    """Provides a transactional scope for session calls.

    See:
        - http://docs.sqlalchemy.org/en/latest/orm/session.html

    Example:

    .. code-block:: python

        class MyController(controllers.Rest):

            def GET(self):
                with transaction_scope(self.db):
                    session.add(Model())
    """
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
