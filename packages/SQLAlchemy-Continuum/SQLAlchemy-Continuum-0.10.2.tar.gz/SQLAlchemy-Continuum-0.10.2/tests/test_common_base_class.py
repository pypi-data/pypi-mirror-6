import sqlalchemy as sa
from tests import TestCase


class TestCommonBaseClass(TestCase):
    def create_models(self):
        class Versioned(object):
            __versioned__ = {
                'base_classes': (self.Model, )
            }

        class TextItem(self.Model, Versioned):
            __tablename__ = 'text_item'

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

        class Article(self.Model, Versioned):
            __tablename__ = 'article'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

        self.TextItem = TextItem
        self.Article = Article

    def test_each_class_has_distinct_translation_class(self):
        class_ = self.TextItem.__versioned__['class']
        assert class_.__name__ == 'TextItemHistory'
        class_ = self.Article.__versioned__['class']
        assert class_.__name__ == 'ArticleHistory'
