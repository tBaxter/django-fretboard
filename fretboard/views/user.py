from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from fretboard.models import Topic
from .general import BaseTopicList


class MemberTopics(BaseTopicList):
    """
    Get the most recent topics created by a user.
    AKA "Your recent topics"
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user_arg = kwargs.get('user', None)
        if user_arg:
            if user_arg.isdigit():
                # we passed an ID
                self.topic_user = get_object_or_404(get_user_model(), id=user_arg)
            else:
                # we passed a username
                self.topic_user = get_object_or_404(get_user_model(), username=user_arg)
        else:
            self.topic_user = request.user
        if not self.topic_user:
            raise Http404
        return super(MemberTopics, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Topic.objects.filter(user_id=self.topic_user.id).select_related('forum')

    def get_context_data(self, **kwargs):
        context = super(MemberTopics, self).get_context_data(**kwargs)
        context.update({
            'forum_slug' : 'user-topics',
            'forum_name' : 'Topics for %s' % self.topic_user.display_name,
        })
        return context
member_topics = MemberTopics.as_view()


class CommentedTopics(MemberTopics):
    """
    Get the most recent topics commented on by a user.
    AKA "Topics you commented on"
    """
    def get_queryset(self):
        if 'topics' in self.request.GET:
            topic_ids = [int(t) for t in self.request.GET['topics'].split(',') if t]
            return Topic.objects.filter(id__in=topic_ids).select_related('forum')
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ft.id FROM forum_topic ft, forum_post fp
            WHERE fp.topic_id = ft.id AND fp.user_id ='{0}'
            GROUP BY ft.id
            ORDER BY ft.id DESC LIMIT 0, 500
            """.format(self.topic_user.id))
        user_post_ids = [row[0] for row in cursor.fetchall()]
        return Topic.objects.filter(id__in=user_post_ids).select_related('forum')

    def get_context_data(self, **kwargs):
        context = super(CommentedTopics, self).get_context_data(**kwargs)
        context.update({
            'forum_slug' : 'recent-topics',
            'forum_name' : "Topics you commented on",
        })
        return context
commented_topics = CommentedTopics.as_view()


class RecentlyViewed(MemberTopics):
    """
    Subclasses MemberTopics to provide topics recently viewed by a given member.
    """

    def get(self, request, *args, **kwargs):
        viewed = request.GET.get('viewed', None)
        if not viewed:
            messages.error(request, "We're unable to retrieve your recently viewed topics")
            return HttpResponseRedirect('/forum/')
        viewed = [int(x) for x in viewed.split(',')]
        self.queryset = Topic.objects.filter(id__in=viewed).select_related('forum')
        return super(RecentlyViewed, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RecentlyViewed, self).get_context_data(**kwargs)
        context.update({
            'forum_slug' : 'recent-viewed',
            'forum_name' : "Recently viewed",
        })
        return context
recently_viewed = RecentlyViewed.as_view()
