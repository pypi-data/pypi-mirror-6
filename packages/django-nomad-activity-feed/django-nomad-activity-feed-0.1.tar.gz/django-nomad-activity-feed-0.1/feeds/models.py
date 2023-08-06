from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Feed(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Follower', symmetrical=False)

    def add_activity(self, model, **kwargs):
        obj = model.objects.create(**kwargs)
        return self.activity_set.add(Activity(content_object=obj))


class Activity(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    pub_date = models.DateTimeField(auto_now_add=True)
    feed = models.ForeignKey(Feed)

    def __unicode__(self):
        return unicode(self.pub_date)

    class Meta:
        ordering = ['-pub_date']


class Follower(models.Model):
    feed = models.ForeignKey(Feed)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = ('feed', 'user')
