# -*- coding: utf-8 -*-
from sqlalchemy import create_engine


def make_engine(**kwargs):
    """Create a new engine for SqlAlchemy.

    Remove the container argument that is sent through from the DI container.
    """
    del kwargs['container']
    return create_engine(**kwargs)
