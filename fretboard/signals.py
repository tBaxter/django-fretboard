import datetime
import time

from django.http import HttpResponse
from django.dispatch import Signal

forum_post_saved = Signal(providing_args=["request", "site_user", "post", "topic"])


def update_forum_votes(sender, **kwargs):
    """
    When a Vote is added, re-saves the topic or post to update vote count.
    Since Votes can be assigned
    to any content type, first makes sure we are dealing with a forum post or topic.
    """
    vote = kwargs['instance']
    if vote.content_type.app_label != "fretboard":
        return
    if vote.content_type.model == "topic":
        from fretboard.models import Topic
        t = Topic.objects.get(id=vote.object.id)
        t.votes = t.get_score()
        t.save()
    elif vote.content_type.model == "post":
        from fretboard.models import Post
        p = Post.objects.get(id=vote.object.id)
        p.votes = p.get_score()
        p.save()


def update_post_relations(sender, **kwargs):
    """ Signal listener for forum_post_saved
        Saves user post count and updates topic last post info
        Usage:
        > from forum.signals import forum_post_saved, update_user_postcount
        > forum_post_saved.connect(update_post_relations)
    """
    site_user             = kwargs['site_user']
    site_user.post_count += 1
    site_user.save()
    now = datetime.datetime.now()
    topic              = kwargs['topic']
    topic.modified     = now
    topic.modified_int = time.time()
    topic.save()

forum_post_saved.connect(update_post_relations)
