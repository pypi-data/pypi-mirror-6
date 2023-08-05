# -*- coding: utf-8 -*-

"""
Models for the "blog" project
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from tagging.fields import TagField
from tagging.models import Tag

from django.conf import settings as conf
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

class Post(models.Model):

    """
    Modelo que define un post.
    """

    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField()
    text = models.TextField(_('Text'))
    tags = TagField()
    image = models.ImageField(_('Image'), upload_to='images/posts', blank=True)
    hits = models.IntegerField(_('Hits'), blank=True, default=1)
    creation_date = models.DateTimeField(_('Creation date'))
    user = models.ForeignKey(User, related_name="post_from")
    highlighted =  models.BooleanField(_('Highlighted'), blank=True)
    status =  models.BooleanField(_('Status'), default=True)
    thread_id = models.CharField(max_length=32, blank=True) # DISQUS

    if "rgallery" in conf.INSTALLED_APPS:
        from rgallery.models import Photo, Video
        photo = models.ManyToManyField(Photo, related_name="photo", blank=True, null=True)
        video = models.ManyToManyField(Video, related_name="myvideo", blank=True, null=True)

    def set_tags(self, tags):
        Tag.objects.update_tags(self, tags)

    def get_tags(self):
        return Tag.objects.get_for_object(self)

    def get_absolute_url(self):
        return reverse('app_blog-post-detail', kwargs={'slug': self.slug})

    def __unicode__(self):
        return self.title

    def valid_comments(self):
        return self.comments.filter(status=1)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')


class Comments(models.Model):

    """
    Modelo que define comentarios (DISQUS).
    """

    comment_id = models.CharField(max_length=32)
    thread_id = models.CharField(max_length=32)
    thread_link = models.CharField(max_length=200)
    forum_id = models.CharField(max_length=32)
    body = models.TextField()
    author_name = models.CharField(max_length=200)
    author_email = models.CharField(max_length=200)
    author_url = models.CharField(max_length=200)
    date = models.DateTimeField()

    def __unicode__(self):
        return "%s - %s" % (self.author_name, self.body)

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
