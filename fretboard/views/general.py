import time
import datetime

from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from fretboard.filters import PostFilter, TopicFilter
from fretboard.models import Forum, Topic, Post

now        = datetime.datetime.now()
pag_by     = settings.PAGINATE_BY


class BaseTopicList(ListView):
    """
    Returns a paginated list of topics in a given forum.
    If it's an ajax request (request has key xhr) it will append the topic list.
    Otherwise, it goes to the topic wrapper.
    """
    template_name = 'fretboard/topic_wrapper.html'
    paginate_by = settings.PAGINATE_BY
    context_object_name = 'topics'

    def dispatch(self, request, *args, **kwargs):
        self.forum_slug = kwargs.get('forum_slug', False)
        self.page       = kwargs.get('page', 1)
        return super(BaseTopicList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            self.template_name = 'fretboard/includes/topic_list.html'
        return super(BaseTopicList, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseTopicList, self).get_context_data(**kwargs)
        context.update({
            'lastseen_time' : self.request.session.get('last_seen', None),
            'page'          : int(self.page)
            })
        return context


class LatestTopics(BaseTopicList):
    """
    Subclasses BaseTopicList to provide topics modified within the past day.
    """
    one_day_ago     = now - datetime.timedelta(days=1)
    one_day_ago_int = time.mktime(one_day_ago.timetuple())
    queryset        = Topic.objects.filter(modified_int__gt=one_day_ago_int).select_related(depth=1)

    def get_context_data(self, **kwargs):
        context = super(LatestTopics, self).get_context_data(**kwargs)
        context.update({
          'forum_slug' : 'latest-topics',
          'forum_name' : "Latest active topics",
          'noadd'      : True
        })
        return context


class TopicList(BaseTopicList):
    """
    Subclasses BaseTopicList to provide topics for a given forum.
    Expects that forum_slug was passed to (and picked up by) BaseTopicList.
    """
    def get_queryset(self):
        self.forum = get_object_or_404(Forum, slug=self.forum_slug)
        return Topic.objects.filter(forum__id=self.forum.id).order_by('-is_sticky', '-modified_int')

    def get_context_data(self, **kwargs):
        context = super(TopicList, self).get_context_data(**kwargs)
        context.update({
          'forum_slug'   : self.forum_slug,
          'forum_name'   : self.forum.name,
          'admin_msg'    : self.forum.message,
        })
        return context


class PostList(ListView):
    """
    Returns a paginated list of posts within a topic.
    If it's an ajax request (request has key xhr) it will append the post list.
    Otherwise, it goes to the post wrapper.
    """
    template_name = 'fretboard/post_wrapper.html'
    paginate_by = settings.PAGINATE_BY
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(topic__id=self.kwargs.get('t_id'))

    def dispatch(self, request, *args, **kwargs):
        self.topic = get_object_or_404(Topic, id=kwargs.get('t_id'))
        self.page  = kwargs.get('page', 1)
        return super(PostList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            self.template_name = 'fretboard/includes/post_list.html'
        return super(PostList, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        forum   = self.topic.forum
        # start number tells the numbered lists where to start counting.
        start_number = int(self.page)
        if start_number > 1:
            start_number = (settings.PAGINATE_BY * (start_number - 1)) + 1

        newpost = None
        if 'last_seen' in self.request.session:
            try:
                # Sort current valid posts by post date, get the first, and only its PK
                newpost = self.get_queryset().filter(post_date__gt=self.request.session['last_seen']).order_by('post_date')[0].pk
            except IndexError:
                pass

        context.update({
            'locked'      : self.topic.is_locked,
            'topic'       : self.topic,
            'topic_id'    : self.topic.id,
            'topic_slug'  : self.topic.slug,
            'start_number': start_number,
            'newpost'     : newpost,
            'page'        : self.page,
            'forum_slug'  : forum.slug,
            'forum_name'  : forum.name
            })
        return context


def filter_search(request):
    """ To do: Rewerite this. """
    topicfilter = TopicFilter(request.GET, queryset=Topic.objects.filter(is_locked=False))
    postfilter  = PostFilter(request.GET, queryset=Post.objects.all().order_by('-topic__id'))
    query       = ''
    search_type = 'default'
    get_string  = ''

    if 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 1
    if 'name' in request.GET or 'text' in request.GET:
        get_string = '&name=%s&text=%s' % (request.GET['name'], request.GET['text'])
        if 'name' in request.GET and request.GET['name'] != '':
            paginator = Paginator(topicfilter.qs, settings.PAGINATE_BY)
            search_type = 'Topic'
            query = request.GET['name']
        elif 'text' in request.GET and request.GET['text'] != '':
            paginator = Paginator(postfilter.qs, settings.PAGINATE_BY)
            search_type = "Post"
            query = request.GET['text']
        if paginator:
            p = paginator.page(page)
            objects = p.object_list
        else:
            return HttpResponse('no queryset found')
        return render(request, 'fretboard/filter_results.html', {
            'object_list': objects,
            'forum_slug': 'search',
            'forum_name': 'Forum search',
            'user': request.user,
            'paginator': paginator,
            'is_paginated': p.has_other_pages(),
            'has_next': p.has_next(),
            'has_previous': p.has_previous(),
            'page': page,
            'next': page + 1,
            'previous': page - 1,
            'pages': paginator.num_pages,
            'hits' : paginator.count,
            'results_per_page': settings.PAGINATE_BY,
            'filter': topicfilter,
            'postfilter': postfilter,
            'search_type': search_type,
            'get_string': get_string,
            'query': query
        })

    return render(request, 'fretboard/filter_results.html', {
        'filter': topicfilter,
        'postfilter': postfilter,
        'search_type': '',
        'object_list': [],
    })
