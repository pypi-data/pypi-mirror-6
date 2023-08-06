from django.views.generic import TemplateView
from django.conf import settings
from djinn_contenttypes.views.base import AcceptMixin
from djinn_news.models.news import News


SHOW_N = getattr(settings, "DJINN_SHOW_N_NEWS_ITEMS", 5)


class NewsViewlet(AcceptMixin, TemplateView):

    template_name = "djinn_news/snippets/news_viewlet.html"

    def news(self, limit=SHOW_N):

        return News.objects.filter(is_global=True).exclude(title=""). \
            order_by('-publish_from', '-changed')[:limit]

    @property
    def show_more(self, limit=SHOW_N):

        return self.news(limit=None).count() > limit
