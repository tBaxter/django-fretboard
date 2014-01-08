import calendar
from datetime import datetime, timedelta

from django import template

from fretboard.helpers import clean_text, format_post as format_post_text
from fretboard.models import Forum, Topic
from fretboard.settings import PAGINATE_BY


def yesterday():
    return datetime.now() - timedelta(days=1)

def yesterday_timestamp():
    return calendar.timegm(yesterday().utctimetuple())

register = template.Library()


@register.assignment_tag
def get_new_topics_count(last_seen=None, for_member=False):
    """
    Returns count of new topics since last visit, or one day.
    {% get_new_topics_count as new_topic_count %}
    """
    if not last_seen:
        last_seen = yesterday()
    if not for_member:
        return Topic.objects.filter(created__gt=last_seen).count()
    return Topic.objects.filter(modified__gt=last_seen, user__id=for_member).count()


@register.assignment_tag
def get_active_topics_count(last_seen_timestamp=None):
    """
    Returns count of new topics since last visit, or one day.
    {% get_active_topics_count as active_topic_count %}
    """
    if not last_seen_timestamp:
        last_seen_timestamp = yesterday_timestamp()
    return Topic.objects.filter(modified_int__gt=last_seen_timestamp).count()


@register.inclusion_tag('fretboard/includes/topic_quick_links.html', takes_context=True)
def topic_quick_links(context, topic, latest, last_seen_time):
    """
    Creates topic listing page links for the given topic, with the given
    number of posts per page.

    Topics with between 2 and 5 pages will have page links displayed for
    each page.

    Topics with more than 5 pages will have page links displayed for the
    first page and the last 3 pages.
    """
    output_text = u''

    if not topic.post_count:
        topic.post_count = topic.post_set.count()
        topic.save(update_fields=['post_count', 'page_count'])

    pages = topic.page_count
    if not pages or pages == 0:
        hits = topic.post_count - 1
        if hits < 1:
            hits = 1
        pages = hits // PAGINATE_BY + 1

    # determine if we need to show new link.
    if latest and latest.get('post_date_int') and latest['post_date_int'] > last_seen_time:
        output_text += '<a href="{0}#first-new-post" class="new">new</a>'.format(topic.get_last_url())

    # If only one post (or none) only return new link, if anything.
    if topic.post_count < 2:
        output_text += '1 post'
    else:
        # We have more than one post. Create last link
        if latest:
            last_link = '<a href="{0}#post-{1}" title="latest post">'.format(topic.get_last_url(), latest['id'])
        else:
            last_link = ''

        # if only one page, just show the number of posts wrapped in a link
        if pages < 2:
            output_text += '{0}{1} posts</a>'.format(last_link, topic.post_count)

        else:
            page_link = u'<a href="%spage%%s/">%%s</a>' % topic.get_short_url()
            if pages < 4:
                page_links = u' '.join([page_link % (page, page) for page in xrange(1, pages + 1)])
            else:
                page_links = u' '.join(
                    [page_link % (1, 1), u'<small>&hellip;</small>'] +
                    [page_link % (page, page) for page in xrange(pages - 1, pages + 1)]
                )
            output_text += '{0}{1}&#9658;</a>'.format(page_links, last_link)

    return {
        'output_text': output_text,
        'topic': topic,
        'forum_slug': context['forum_slug'],
        'user': context['user'],
        'perms': context['perms']
    }


@register.filter
def format_post(value):
    """
    Normally post formatting will be handled on save.
    However, in some cases, such as forum archive, we'll do it real-time.
    """
    text = clean_text(value)
    return format_post_text(text)


@register.assignment_tag
def get_topic_list(num=10, top_items=False):
    """
    Returns a list of top recent topics, excluding less valuable forums.
    Default is 10 topics.
    Can be sorted for most active topics by votes and post count.
    Usage:
    {% get_topic_list 5 as topics %}
    {% get_topic_list 7 top_items=True as topics %}
    """
    excluded_forum_ids = [3, 7, 10, 12, 15, 16, 17, 18, 19, 23]
    topics = Topic.objects.exclude(forum_id__in=excluded_forum_ids).order_by('-id')[0:num]
    if top_items:
        topics = sorted(list(topics), key=lambda t: (t.forum_id, -t.votes, -t.post_count))
    return topics


class ForumNameNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def __repr__(self):
        return "<Forum Node>"

    def render(self, context):
        context[self.varname] = Forum.objects.values('name', 'slug', 'category__name')
        return ''


class GetForumNames:
    """
    {% get_forum_list as forum_list %}
    """
    def __init__(self, tag_name):
        self.tag_name = tag_name

    def __call__(self, parser, token):
        bits = token.contents.split()
        if len(bits) != 3:
            raise template.TemplateSyntaxError, "'%s' tag takes two arguments" % bits[0]
        if bits[1] != "as":
            raise template.TemplateSyntaxError, "First argument to '%s' tag must be 'as'" % bits[0]
        return ForumNameNode(bits[2])


register.tag('get_forum_list', GetForumNames('get_forum_list'))
