from copy import copy
import inspect
import itertools as it
import os
import warnings
import sqlalchemy as sa
from six import PY3
from pytest import mark
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_continuum import make_versioned, versioning_manager
from sqlalchemy_continuum.ext.flask import (
    versioning_manager as flask_versioning_manager
)


warnings.simplefilter('error', sa.exc.SAWarning)


make_versioned(options={'strategy': 'subquery'})


class QueryPool(object):
    queries = []


@sa.event.listens_for(sa.engine.Engine, 'before_cursor_execute')
def log_sql(
    conn,
    cursor,
    statement,
    parameters,
    context,
    executemany
):
    QueryPool.queries.append(statement)


# @mark.skipif("PY3 and os.environ.get('DB') == 'mysql'")
class TestCase(object):
    versioning_strategy = 'subquery'
    transaction_column_name = 'transaction_id'
    end_transaction_column_name = 'end_transaction_id'
    track_property_modifications = False
    store_data_at_delete = False
    composite_pk = False

    @property
    def options(self):
        return {
            'base_classes': (self.Model, ),
            'strategy': self.versioning_strategy,
            'transaction_column_name': self.transaction_column_name,
            'end_transaction_column_name': self.end_transaction_column_name,
            'track_property_modifications': self.track_property_modifications,
            'store_data_at_delete': self.store_data_at_delete
        }

    def setup_class(cls):
        versioning_manager.options['versioning'] = True
        flask_versioning_manager.options['versioning'] = False

    def setup_method(self, method):
        adapter = os.environ.get('DB', 'postgres')
        if adapter == 'postgres':
            dns = 'postgres://postgres@localhost/sqlalchemy_continuum_test'
        elif adapter == 'mysql':
            dns = 'mysql+pymysql://travis@localhost/sqlalchemy_continuum_test'
        elif adapter == 'sqlite':
            dns = 'sqlite:///:memory:'
        else:
            raise Exception('Unknown driver given: %r' % adapter)

        self.engine = create_engine(dns)
        # self.engine.echo = True
        self.connection = self.engine.connect()
        self.Model = declarative_base()

        self.create_models()

        sa.orm.configure_mappers()

        if hasattr(self, 'Article'):
            self.ArticleHistory = self.Article.__versioned__['class']
        if hasattr(self, 'Tag'):
            try:
                self.TagHistory = self.Tag.__versioned__['class']
            except (AttributeError, KeyError):
                pass
        self.create_tables()

        Session = sessionmaker(bind=self.connection)
        self.session = Session()

    def create_tables(self):
        self.Model.metadata.create_all(self.connection)

    def drop_tables(self):
        self.Model.metadata.drop_all(self.connection)

    def teardown_method(self, method):
        QueryPool.queries = []
        versioning_manager.reset()
        versioning_manager.uow.reset()

        self.session.close_all()
        self.session.expunge_all()
        self.drop_tables()
        self.engine.dispose()
        self.connection.close()

    def create_models(self):
        class Article(self.Model):
            __tablename__ = 'article'
            __versioned__ = copy(self.options)

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)
            content = sa.Column(sa.UnicodeText)
            description = sa.Column(sa.UnicodeText)

        class Tag(self.Model):
            __tablename__ = 'tag'
            __versioned__ = copy(self.options)

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255))
            article_id = sa.Column(sa.Integer, sa.ForeignKey(Article.id))
            article = sa.orm.relationship(Article, backref='tags')

        self.Article = Article
        self.Tag = Tag


setting_variants = {
    'versioning_strategy': ['subquery', 'validity'],
    'store_data_at_delete': [True, False],
    'track_property_modifications': [True, False],
    'transaction_column_name': ['transaction_id', 'tx_id'],
    'end_transaction_column_name': ['end_transaction_id', 'end_tx_id']
}


def create_test_cases(base_class, setting_variants=setting_variants):
    """
    Function for creating bunch of test case classes for given base class
    and setting variants. Number of test cases created is the number of linear
    combinations with setting variants.

    :param base_class:
        Base test case class, should be in format 'xxxTestCase'
    :param setting_variants:
        A dictionary with keys as versioned configuration option keys and
        values as list of possible option values.
    """
    names = sorted(setting_variants)
    combinations = [
        dict(zip(names, prod))
        for prod in
        it.product(*(setting_variants[name] for name in names))
    ]

    # Get the module where this function was called in.
    frm = inspect.stack()[1]
    module = inspect.getmodule(frm[0])

    class_suffix = base_class.__name__[0:-len('TestCase')]
    for index, combination in enumerate(combinations):
        class_name = 'Test%s%i' % (class_suffix, index)
        # Assign a new test case class for current module.
        setattr(
            module,
            class_name,
            type(
                class_name,
                (base_class, ),
                combination
            )
        )
