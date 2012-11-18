import datetime
import time

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from fretboard.models import Forum, Topic

now = datetime.datetime.now()
one_day_ago     = now - datetime.timedelta(days=1)
one_day_ago_int = time.mktime(one_day_ago.timetuple())

register = template.Library()


class TopicListNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = Topic.objects.order_by('-created_int')[:7]
        return ''


class GetTopicList:
    """
    {% get_topic_list as topic_list %}
    """
    def __init__(self, tag_name):
        self.tag_name = tag_name

    def __call__(self, parser, token):
        bits = token.contents.split()
        if len(bits) != 3:
            raise template.TemplateSyntaxError, "'%s' tag takes two arguments" % bits[0]
        if bits[1] != "as":
            raise template.TemplateSyntaxError, "First argument to '%s' tag must be 'as'" % bits[0]
        return TopicListNode(bits[2])


class TopicsCount(template.Node):
    def __init__(self, request, varname):
        self.varname = varname
        self.request = template.Variable(request)

    def render(self, context):
        new     = None
        latest  = Topic.objects.filter(modified_int__gt=one_day_ago_int).count()
        try:
            request = self.request.resolve(context)
        except:
            return
        if request.user and request.user.is_authenticated and 'last_seen_timestamp' in request.session:
            lastseen_time = request.session['last_seen_timestamp']
            new = Topic.objects.filter(modified_int__gt=lastseen_time).count()
        context[self.varname] = [latest, new]
        return ''


class GetTopicCounts:
    """
    {% get_topic_counts <user> as topic_counts %}
    """
    def __init__(self, tag_name):
        self.tag_name = tag_name

    def __call__(self, parser, token):
        bits = token.contents.split()
        if len(bits) != 4:
            raise template.TemplateSyntaxError, "'%s' tag takes two arguments" % bits[0]
        if bits[2] != "as":
            raise template.TemplateSyntaxError, "First argument to '%s' tag must be 'as'" % bits[0]
        return TopicsCount(bits[1], bits[3])


@register.filter
def topic_pagination(topic):
    """
    Creates topic listing page links for the given topic, with the given
    number of posts per page.

    Topics with between 2 and 5 pages will have page links displayed for
    each page.

    Topics with more than 5 pages will have page links displayed for the
    first page and the last 3 pages.
    """
    post_count = topic.post_set.count()
    hits = post_count - 1
    if hits < 1:
        hits = 1
    pages = hits // settings.PAGINATE_BY + 1

    if pages < 2:
        html = u'%s posts' % post_count
    else:
        page_link = u'<a class="pagelink" href="%spage%%s/">%%s</a>' % \
            topic.get_short_url()
        if pages < 4:
            html = u' '.join([page_link % (page, page) \
                              for page in xrange(1, pages + 1)])
        else:
            html = u' '.join([page_link % (1, 1), u'&hellip;'] + \
                [page_link % (page, page) \
                 for page in xrange(pages - 1, pages + 1)])
    return mark_safe(html)


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


register.tag('get_topic_counts', GetTopicCounts('get_topic_counts'))
register.tag('get_topic_list', GetTopicList('get_topic_list'))
register.tag('get_forum_list', GetForumNames('get_forum_list'))
