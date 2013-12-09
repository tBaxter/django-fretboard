from django.conf import settings
from django.db import models
from django.db.models import signals

from .signals import update_forum_votes
from .helpers import clean_text, format_post

from voting.models import Vote

UserModel = getattr(settings, "AUTH_USER_MODEL", "auth.User")
PAGINATE_BY = getattr(settings, "PAGINATE_BY", 25)


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
        """
        Return forum names and slugs for the current category.
        """
        return self.forum_set.values('slug', 'name')


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
        return ('topic_list', [str(self.slug)])

    def get_recent(self):
        return self.topic_set.all().order_by('-id')[:3]


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

    user             = models.ForeignKey(UserModel, blank=True, null=True, editable=False)
    author           = models.CharField(max_length=255, blank=True)
    post_count       = models.PositiveIntegerField(default=1, editable=False)
    lastpost         = models.CharField(max_length=255, verbose_name="Last Post", blank=True)
    latest_post      = models.ForeignKey('fretboard.Post', blank=True, null=True, related_name="latest_post", editable=False)
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
        Save page count locally on the object for quick reference,
        but only after the first save.
        """
        if self.id:
            self.page_count = self.get_page_max()
            if not self.permalink:
                self.permalink = self.get_absolute_url()
        super(Topic, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns full url for topic, with page number.
        Also used to create static permalink
        """
        if self.permalink:
            return self.permalink
        return "%spage1/" % (self.get_short_url())

    @models.permalink
    def get_short_url(self):
        """ Returns short version of topic url (without page number) """
        return ('post_short_url', [self.forum.slug, self.slug, str(self.id)])

    def get_last_url(self):
        """ Returns link to last page of topic """
        return '%spage%s/' % (self.get_short_url(), self.get_page_max())

    def get_page_max(self):
        page_by        = PAGINATE_BY
        postcount      = self.post_set.count()
        max_pages      = (postcount / page_by) + 1
        if postcount % page_by == 0:
            max_pages   = postcount / page_by
        return max_pages

    def get_mod_time(self):
        return self.post_set.latest('id').post_date

    def get_latest_post(self):
        """
        Attempts to get most recent post in a topic.
        Returns none if it fails.
        """
        try:
            latest = self.post_set.values('id', 'post_date', 'author_name', 'post_date_int').latest('id')
        except:
            latest = None
        return latest

    def get_score(self):
        return Vote.objects.get_score(self)['score']

    def get_post_count(self):
        return self.post_set.count()


class Post(models.Model):
    topic          = models.ForeignKey(Topic)
    text           = models.TextField()
    text_formatted = models.TextField(blank=True)
    author         = models.ForeignKey(UserModel)
    author_name    = models.CharField(max_length=255, verbose_name="Author Preferred Name", blank=True, null=True)
    avatar         = models.CharField(max_length=255, verbose_name="Author Avatar", blank=True, null=True)
    post_date      = models.DateTimeField(auto_now_add=True)
    post_date_int  = models.IntegerField(editable=False, null=True, help_text="Stores an integer of post_date as ordinal + hour for faster searching")
    quote          = models.ForeignKey('self', null=True, blank=True)
    # to do... use contentImage?
    image          = models.ImageField(upload_to='img/fretboard/%Y/', blank=True, null=True)
    topic_page     = models.IntegerField(blank=True, null=True, default=1)
    votes          = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        get_latest_by = "id"
        ordering      = ('id',)
        db_table      = 'forum_post'

    def __unicode__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        """
        Save page count locally on the object for quick reference,
        but only after the first save.
        """
        self.text = clean_text(self.text)
        self.text_formatted = format_post(self.text)
        super(Post, self).save(*args, **kwargs)

    def get_score(self):
        return Vote.objects.get_score(self)['score']

    def get_avatar(self):
        return '/media/' + str(self.post_author.avatar)


signals.post_save.connect(update_forum_votes, sender=Vote)
