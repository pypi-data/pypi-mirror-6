import sqlalchemy as sa
from tests import TestCase


class TestCommonBaseClass(TestCase):
    def create_models(self):
        class TextItem(self.Model):
            __tablename__ = 'text_item'
            __versioned__ = {}

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

        class ArticleHistoryBase(self.Model):
            __abstract__ = True

        class Article(self.Model):
            __tablename__ = 'article'
            __versioned__ = {
                'base_classes': (ArticleHistoryBase, )
            }
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

        self.TextItem = TextItem
        self.Article = Article
        self.ArticleHistoryBase = ArticleHistoryBase

    def test_each_class_has_distinct_translation_class(self):
        class_ = self.TextItem.__versioned__['class']
        assert class_.__name__ == 'TextItemHistory'
        class_ = self.Article.__versioned__['class']
        assert class_.__name__ == 'ArticleHistory'
        assert issubclass(class_, self.ArticleHistoryBase)
