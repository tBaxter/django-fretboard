from django.conf import settings
from django.db import models
from django.db.models import signals

from fretboard.signals import update_forum_votes
from sorl.thumbnail.fields import ImageWithThumbnailsField
from voting.models import Vote


class Category(models.Model):
    """
    Top level organization, allowing for grouping for forums.
    """
    name = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        db_table      = 'forum_category'

    def __unicode__(self):
        return self.name

    def get_forum_names(self):
        return self.forum_set.values('forum_slug', 'forum_name')


class Forum(models.Model):
    """
    Groups and organizes topics. Admin-created.
    """
    category            = models.ForeignKey(Category, verbose_name="Forum Category")
    name                = models.CharField(max_length=255, verbose_name="Forum Name")
    slug                = models.SlugField(max_length=255)
    description         = models.CharField(max_length=255, verbose_name="Forum Description")
    order               = models.PositiveSmallIntegerField(default=0, help_text="Order of forums on the category list")
    message             = models.TextField('Admin message', blank=True, help_text="If you need to post a message for all of the forum")
    is_closed           = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table      = 'forum_forum'

    @models.permalink
    def get_absolute_url(self):
        return ('forum_topic_list', [str(self.slug)])

    def get_recent(self):
        return self.topic_set.values().order_by('-id')[:3]


class Topic(models.Model):
    """
    Topics within a forum. User-created.
    """
    forum            = models.ForeignKey(Forum)
    name             = models.CharField(max_length=255, verbose_name="Topic Title")
    slug             = models.SlugField(max_length=255)

    created          = models.DateTimeField(auto_now_add=True)
    created_int      = models.IntegerField(editable=False, help_text="Stores created as ordinal + hour as an integer for faster searching")
    modified         = models.DateTimeField(auto_now_add=True, help_text="Will be manually changed so every edit doesn't alter the modified time.")
    modified_int     = models.IntegerField(editable=False, help_text="Stores modified as ordinal + hour as an integer for faster searching")

    is_sticky        = models.BooleanField(blank=True, default=False)
    is_locked        = models.BooleanField(blank=True, default=False)

    author           = models.CharField(max_length=255, blank=True)
    post_count       = models.PositiveIntegerField(default=1)
    lastpost         = models.CharField(max_length=255, verbose_name="Last Post", blank=True)
    latest_post      = models.ForeignKey('fretboard.Post', blank=True, null=True, related_name="latest_post")
    lastpost_author  = models.CharField(max_length=255)
    page_count       = models.PositiveIntegerField(default=1)
    permalink        = models.CharField(max_length=255, blank=True)
    votes            = models.IntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table      = 'forum_topic'
        ordering      = ['-modified_int']

    def save(self, *args, **kwargs):
        """
        Saves page count locally on the object for quick reference,
        but only after the first save.
        """
        if self.id:
            self.page_count = self.get_page_max()
            if not self.permalink:
                self.permalink = self.get_absolute_url()
        super(Topic, self).save()

    def get_absolute_url(self):
        return "%spage1/" % (self.get_short_url())

    @models.permalink
    def get_short_url(self):
        return ('post_short_url', [self.forum.slug, self.slug, str(self.id)])

    def get_page_max(self):
        page_by        = settings.PAGINATE_BY
        postcount      = self.post_set.count()
        max_pages      = (postcount / page_by) + 1
        if postcount % page_by == 0:
            max_pages   = postcount / page_by
        return max_pages

    def get_mod_time(self):
        return self.post_set.latest('id').post_date

    def get_latest_post(self):
        return self.post_set.values('id', 'post_date', 'author_name', 'post_date_int').latest('id')

    def get_score(self):
        return Vote.objects.get_score(self)['score']

    def get_post_count(self):
        return self.post_set.count()


class Post(models.Model):
    topic          = models.ForeignKey(Topic)
    text           = models.TextField()
    text_formatted = models.TextField(blank=True)
    author         = models.ForeignKey(settings.AUTH_USER_MODEL)
    author_name    = models.CharField(max_length=255, verbose_name="Author Preferred Name", blank=True, null=True)
    avatar         = models.CharField(max_length=255, verbose_name="Author Avatar", blank=True, null=True)
    post_date      = models.DateTimeField(auto_now_add=True)
    post_date_int  = models.IntegerField(editable=False, null=True, help_text="Stores an integer of post_date as ordinal + hour for faster searching")
    quote          = models.ForeignKey('self', null=True, blank=True)

    image          = ImageWithThumbnailsField(
        upload_to='img/board_pics/%Y/', blank=True, null=True,
        thumbnail={'size': (700, 700)},
        extra_thumbnails={
        'icon': {'size': (50, 75), 'options': {'autocrop': True, 'crop': (0, -0), 'upscale': True}},
        'mobile': {'size': (480, 480)},
        },
    )
    topic_page     = models.IntegerField(blank=True, null=True)
    votes          = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        get_latest_by = "id"
        ordering      = ('id',)
        db_table      = 'forum_post'

    def __unicode__(self):
        return str(self.id)

    def get_score(self):
        return Vote.objects.get_score(self)['score']

    def get_avatar(self):
        return '/media/' + str(self.post_author.avatar)


signals.post_save.connect(update_forum_votes, sender=Vote)
