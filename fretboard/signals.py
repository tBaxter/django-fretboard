from django.db.models import get_model


#forum_post_saved = Signal(providing_args=["request", "site_user", "post", "topic"])


def update_forum_votes(sender, **kwargs):
    """
    When a Vote is added, re-saves the topic or post to update vote count.
    Since Votes can be assigned
    to any content type, first makes sure we are dealing with a forum post or topic.

    Deprecated 1-6-14 by storing score as cached property
    """
    vote = kwargs['instance']
    if vote.content_type.app_label != "fretboard":
        return
    if vote.content_type.model == "topic":
        t = get_model('fretboard', 'Topic').objects.get(id=vote.object.id)
        t.votes = t.score()
        t.save(update_fields=['votes'])
    elif vote.content_type.model == "post":
        p = get_model('fretboard', 'Post').objects.get(id=vote.object.id)
        p.votes = p.score()
        p.save(update_fields=['votes'])
