from djinn_news.models.news import News
from haystack import indexes
from pgsearch.base import ContentSearchIndex


class NewsIndex(ContentSearchIndex, indexes.Indexable):

    published = indexes.DateTimeField(model_attr='publish_from', null=True)

    def prepare_published(self, obj):
        return obj.date

    def get_model(self):

        return News
