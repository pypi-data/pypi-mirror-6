# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from armet.connectors.flask import resources as flask_resources
from armet.connectors.sqlalchemy import resources as sqlalchemy_resources
from alchemist import db

__all__ = [
    'Resource',
    'ModelResource',
]


class Resource(flask_resources.Resource):

    @property
    def session(self):
        return db.session

    def route(self, *args, **kwargs):
        try:
            # Continue on with the cycle.
            result = super(Resource, self).route(*args, **kwargs)

            # Commit the session.
            db.session.commit()

            # Return the result.
            return result

        except:
            # Something occurred; rollback the session.
            db.session.rollback()

            # Re-raise the exception.
            raise


class ModelResourceOptions(object):

    def __init__(self, meta, name, bases):
        #! SQLAlchemy session used to perform operations on the models.
        self.session = db.session


class ModelResource(sqlalchemy_resources.ModelResource):

    def route(self, *args, **kwargs):
        return Resource.route(self, *args, **kwargs)
