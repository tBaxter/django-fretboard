from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from easy_thumbnails.fields import ThumbnailerImageField
from tango_shared.models import set_img_path, BaseUserContentModel
from voting.models import Vote

from .managers import TopicManager


def get_paginate_by():
    from .settings import PAGINATE_BY
    return PAGINATE_BY


class Category(models.Model):
    """
    Top level organization, allowing for grouping for forums.
    """
    name = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        db_table = 'forum_category'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_forum_names(self):
        """
        Return forum names and slugs for the current category.
        """
        return self.forum_set.values('slug', 'name')


class Forum(models.Model):
    """
    Groups and organizes topics. Admin-created.
    """
    category = models.ForeignKey(
        Category, 
        verbose_name="Forum Category", 
        on_delete="CASCADE"
    )
    name = models.CharField(max_length=255, verbose_name="Forum Name")
    slug = models.SlugField(max_length=255)
    description = models.CharField(max_length=255, verbose_name="Forum Description")
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Order of forums on the category list"
    )
    message = models.TextField(
        'Admin message',
        blank=True,
        help_text="If you need to post a message for all of the forum"
    )
    is_closed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'forum_forum'

    @models.permalink
    def get_absolute_url(self):
        return ('topic_list', [str(self.slug)])

    def get_recent(self):
        return self.topic_set.all().order_by('-id')[:3]


class Topic(models.Model):
    """
    Topics within a forum. User-created.

    Created and modified are stored as both datetime objects and as an ordinal+hour integer
    because querying by int is faster, especially in Mysql. See:
    http://stackoverflow.com/questions/4594229/mysql-integer-vs-datetime-index

    """
    forum = models.ForeignKey(Forum, on_delete="CASCADE")
    name = models.CharField(max_length=255, verbose_name="Topic Title")
    slug = models.SlugField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    created_int = models.IntegerField(
        editable=False,
        help_text="Stores created as ordinal + hour as an integer for faster searching"
    )
    modified = models.DateTimeField(
        auto_now_add=True,
        help_text="Will be manually changed so every edit doesn't alter the modified time."
    )
    modified_int = models.IntegerField(
        editable=False,
        help_text="Stores modified as ordinal + hour as an integer for faster searching"
    )

    is_sticky = models.BooleanField(blank=True, default=False)
    is_locked = models.BooleanField(blank=True, default=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        blank=True, null=True, 
        editable=False, 
        on_delete="CASCADE"
    )

    redirect_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="If set, traffic to this topic will redirect to the given URL."
    )

    objects = TopicManager()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'forum_topic'
        ordering = ['-modified_int']

    def get_absolute_url(self):
        """
        Returns URL to first page of topic.
        Note that for any page within a topic, a canonical URL will be available.
        """
        return "{0}page1/".format(self.get_short_url())

    @models.permalink
    def get_short_url(self):
        """ Returns short version of topic url (without page number) """
        return ('post_short_url', [self.forum.slug, self.slug, str(self.id)])

    @cached_property
    def last_url(self):
        """ Returns link to last page of topic """
        return '{0}page{1}/'.format(self.get_short_url(), self.page_count)

    @cached_property
    def latest_post(self):
        """
        Attempts to get most recent post in a topic.
        Returns none if it fails.
        """
        try:
            return self.post_set.latest('post_date')
        except Post.DoesNotExist:
            return None

    @cached_property
    def first_post(self):
        """
        Attempts to get first post in a topic.
        Returns none if it fails.
        """
        try:
            return self.post_set.all()[0]
        except IndexError:
            return None

    @cached_property
    def page_count(self):
        """
        Get count of total pages
        """
        postcount = self.post_set.count()
        max_pages = (postcount / get_paginate_by())
        if postcount % get_paginate_by() != 0:
            max_pages += 1
        return max_pages

    @cached_property
    def post_count(self):
        return self.post_set.count()

    @cached_property
    def votes(self):
        return Vote.objects.get_score(self)['score']

    @cached_property
    def author(self):
        try:
            return self.post_set.all()[0].user
        except IndexError:
            return None

    def get_image(self):
        """
        Gets first image from post set.
        """
        posts_with_images = self.post_set.filter(image__gt='')
        if posts_with_images:
            return posts_with_images[0].image


class Post(BaseUserContentModel):
    """
    Post text is cleaned on save() through the BaseUserContentModel
    """
    topic = models.ForeignKey(Topic, on_delete="CASCADE")
    post_date_int = models.IntegerField(
        editable=False,
        null=True,
        help_text="Stores an integer of post_date as ordinal + hour for faster searching."
    )
    quote = models.ForeignKey('self', null=True, blank=True, on_delete="CASCADE")

    image = ThumbnailerImageField(
        upload_to=set_img_path,
        help_text="Image size should be a minimum of 720px and no more than 2000px wide.",
        blank=True,
        null=True
    )

    class Meta:
        get_latest_by = "id"
        ordering = ('id',)
        db_table = 'forum_post'

    def __str__(self):
        return self.topic

    def get_absolute_url(self):
        return self.post_url

    @cached_property
    def post_url(self):
        """
        Determine which page this post lives on within the topic
        and return link to anchor within that page
        """
        topic = self.topic
        topic_page = topic.post_set.filter(id__lt=self.id).count() / get_paginate_by() + 1
        return "{0}page{1}/#post-{2}".format(topic.get_short_url(), topic_page, self.id)

    @cached_property
    def author(self):
        """
        Convenience alias from user to 'author'
        """
        return self.user

    @cached_property
    def author_display_name(self):
        return self.user.display_name

    @cached_property
    def avatar(self):
        try:
            avatar_url = self.user.avatar.url
        except ValueError:  # catch avatar url does not exist
            avatar_url = '%s/img/avatars/default.jpg' % settings.MEDIA_URL
        return avatar_url

    @cached_property
    def parent(self):
        """
        Shortcut to parent topic. Makes life easier for activity monitor.
        """
        return self.topic
