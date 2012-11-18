from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404

from fretboard.models import Topic
from fretboard.views.general import BaseTopicList

UserModel      = get_user_model()
pag_by         = settings.PAGINATE_BY
last_seen_time = None


class RecentlyViewed(BaseTopicList):
    """
    Subclasses BaseTopicList to provide topics recently viewed by a given member.
    """
    def post(self, request, *args, **kwargs):
        if not 'viewed' in request.POST:
            messages.error(request, "We're unable to retrieve your recently viewed topics")
            return HttpResponseRedirect('/forum/')
        viewed = request.POST['viewed'].split(',')
        self.queryset = Topic.objects.filter(id__in=viewed).select_related()
        return super(RecentlyViewed, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RecentlyViewed, self).get_context_data(**kwargs)
        context.update({
          'forum_slug' : 'recent-viewed',
          'forum_name' : "Recently viewed",
          'noadd'      : True
        })
        return context


class SinceLastVisit(BaseTopicList):
    """
    Returns list of topics that are new since the user was last seen.
    """
    def get_queryset(self):
        last_seen_int  = self.request.session['last_seen_timestamp']
        return Topic.objects.filter(modified_int__gt=last_seen_int).select_related()

    def get_context_data(self, **kwargs):
        context = super(SinceLastVisit, self).get_context_data(**kwargs)
        context.update({
          'forum_slug' : 'new-topics',
          'forum_name' : "Since your last visit",
          'noadd'      : True
        })
        return context


class MemberTopics(BaseTopicList):
    """
    Get the most recent topics created by a user.
    AKA "Your recent topics"
    """
    def dispatch(self, request, *args, **kwargs):
        user_arg = kwargs.get('user', None)
        if user_arg:
            if user_arg.isdigit():  # we passed an ID
                self.commenter = get_object_or_404(UserModel, id=user_arg)
            else:  # we passed a username
                self.commenter = get_object_or_404(UserModel, username=user_arg)
        else:
            self.commenter = request.user
        if not self.commenter:
            raise Http404
        return super(MemberTopics, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'topics' in request.POST:
            topic_ids = request.POST['topics'].split(',')
            topics    = Topic.objects.filter(id__in=topic_ids).select_related()
        else:  # Have to do this the hard way.
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("""
                SELECT ft.id FROM forum_topic ft, forum_post fp
                WHERE fp.topic_id = ft.id AND fp.author_id ='{0}'
                GROUP BY ft.id
                ORDER BY ft.id DESC LIMIT 0, 500
                """.format(self.commenter.id))
            user_post_ids = [row[0] for row in cursor.fetchall()]
            topics = Topic.objects.filter(id__in=user_post_ids).select_related()
        self.queryset = topics
        return super(MemberTopics, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MemberTopics, self).get_context_data(**kwargs)
        context.update({
          'forum_slug' : 'recent-topics',
          'forum_name' : "Your recent topics",
          'noadd'      : True
        })
        return context

