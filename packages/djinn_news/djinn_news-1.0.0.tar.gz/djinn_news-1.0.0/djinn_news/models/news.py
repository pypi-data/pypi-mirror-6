from django.db import models
from django.utils.translation import ugettext_lazy as _
from djinn_contenttypes.registry import CTRegistry
from djinn_contenttypes.models.publishable import PublishableContent
from djinn_contenttypes.models.attachment import ImgAttachment
from djinn_contenttypes.models.commentable import Commentable


class News(PublishableContent, Commentable):

    """ News content type """

    text = models.TextField(null=True, blank=True)

    images = models.ManyToManyField(ImgAttachment)

    show_images = models.BooleanField(default=True)

    is_global = models.BooleanField(default=False)

    def documents(self):

        return self.get_related(relation_type="related_document")

    @property
    def date(self):

        return self.publish_from or self.created

    class Meta:
        app_label = "djinn_news"


CTRegistry.register(
    "news",
    {"class": News,
     "app": "djinn_news",
     "group_add": True,
     "label": _("News")}
    )
