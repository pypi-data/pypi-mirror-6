from django.views.generic import TemplateView
from django.conf import settings
from djinn_contenttypes.views.base import AcceptMixin
from djinn_news.models.news import News
from datetime import datetime
from django.db.models.query import Q

SHOW_N = getattr(settings, "DJINN_SHOW_N_NEWS_ITEMS", 5)


class NewsViewlet(AcceptMixin, TemplateView):

    template_name = "djinn_news/snippets/news_viewlet.html"

    def news(self, limit=SHOW_N):

        now = datetime.now()
        # only return News items in currently published state
        # and having at least a title
        return News.objects.filter(is_global=True). \
            filter(publish_from__lt=now). \
            filter(Q(publish_to__isnull=True)|Q(publish_to__lt=now)). \
            exclude(title=""). \
            order_by('-publish_from', '-changed')[:limit]

    @property
    def show_more(self, limit=SHOW_N):

        return self.news(limit=None).count() > limit
