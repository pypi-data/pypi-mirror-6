from datetime import datetime
import sqlalchemy as sa
from sqlalchemy_continuum import changeset
from sqlalchemy_continuum.utils import is_modified

from tests import TestCase


class TestChangeSet(TestCase):
    def test_changeset_for_new_value(self):
        article = self.Article(name=u'Some article')
        assert changeset(article) == {'name': [u'Some article', None]}

    def test_changeset_for_deletion(self):
        article = self.Article(name=u'Some article')
        self.session.add(article)
        self.session.commit()
        self.session.delete(article)
        assert changeset(article) == {'name': [None, u'Some article']}

    def test_changeset_for_update(self):
        article = self.Article(name=u'Some article')
        self.session.add(article)
        self.session.commit()
        article.tags
        article.name = u'Updated article'
        assert changeset(article) == {
            'name': [u'Updated article', u'Some article']
        }


class TestIsModified(TestCase):
    def create_models(self):
        class Article(self.Model):
            __tablename__ = 'article'
            __versioned__ = {
                'exclude': 'content'
            }
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255))
            created_at = sa.Column(sa.DateTime, default=datetime.now)
            content = sa.Column(sa.Unicode(255))

        self.Article = Article

    def test_included_column(self):
        article = self.Article(name=u'Some article')
        assert is_modified(article)

    def test_excluded_column(self):
        article = self.Article(content=u'Some content')
        assert not is_modified(article)

    def test_auto_assigned_datetime_exclusion(self):
        article = self.Article(created_at=datetime.now())
        assert not is_modified(article)
