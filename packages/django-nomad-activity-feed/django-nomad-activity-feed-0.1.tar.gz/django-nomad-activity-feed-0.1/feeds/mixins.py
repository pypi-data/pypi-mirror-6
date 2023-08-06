from django.db import models
from django.contrib.contenttypes.models import ContentType
from feeds.models import Feed


class FeedMixin(object):
    activity_feed = models.ForeignKey('feeds.Feed', related_name='+', null=True, blank=True)

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self)

    @property
    def feed(self):
        if self.pk:
            return Feed.objects.get_or_create(content_type=self.content_type, object_id=self.pk)[0]

    @property
    def followers(self):
        return self.feed.followers.all()






