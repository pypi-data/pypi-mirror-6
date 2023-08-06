from __future__ import absolute_import

from flask import request
from flask.globals import _app_ctx_stack, _request_ctx_stack
from flask.ext.login import current_user
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

from ..transaction_log import TransactionLogBase as _TransactionLogBase
from ..manager import VersioningManager


def fetch_current_user_id(self):
    # Return None if we are outside of request context.
    if _app_ctx_stack.top is None or _request_ctx_stack.top is None:
        return
    try:
        return current_user.id
    except AttributeError:
        return


def fetch_remote_addr(self):
    # Return None if we are outside of request context.
    if _app_ctx_stack.top is None or _request_ctx_stack.top is None:
        return
    return request.remote_addr


class TransactionLogBase(_TransactionLogBase):
    remote_addr = sa.Column(sa.String(50), default=fetch_remote_addr)

    @declared_attr
    def user_id(self):
        return sa.Column(
            sa.Integer,
            sa.ForeignKey('user.id'),
            default=fetch_current_user_id,
            index=True
        )

    @declared_attr
    def user(self):
        return sa.orm.relationship('User')


class FlaskVersioningManager(VersioningManager):
    def __init__(self, options={}):
        options.setdefault('transaction_log_base', TransactionLogBase)
        VersioningManager.__init__(self, options=options)


versioning_manager = FlaskVersioningManager()
