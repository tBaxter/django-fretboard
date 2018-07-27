import time
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView

from fretboard.filters import PostFilter, TopicFilter
from fretboard.forms import PostForm
from fretboard.models import Forum, Topic, Post
from fretboard.settings import PAGINATE_BY, FORUM_BASE_NAME


class CategoryList(ListView):
    """
    Returns a list of Forums ordered by category.
    """
    template_name="fretboard/category_list.html"
    context_object_name="forums"
    queryset=Forum.objects.all().order_by('category')

    def get_context_data(self, **kwargs):
        context = super(CategoryList, self).get_context_data(**kwargs)
        context.update({
            'FORUM_BASE_NAME' : FORUM_BASE_NAME
        })
        return context
category_list = CategoryList.as_view()

class BaseTopicList(ListView):
    """
    Returns a paginated list of topics in a given forum.
    If it's an ajax request (request has key xhr) it will append the topic list.
    Otherwise, it goes to the topic wrapper.
    """
    template_name = 'fretboard/topic_wrapper.html'
    paginate_by = PAGINATE_BY
    context_object_name = 'topics'

    def dispatch(self, request, *args, **kwargs):
        self.forum_slug = kwargs.get('forum_slug', False)
        self.page       = kwargs.get('page', request.GET.get('page'))
        if not self.page:
            self.page = 1
        return super(BaseTopicList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            self.template_name = 'fretboard/includes/topic_list.html'
        return super(BaseTopicList, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseTopicList, self).get_context_data(**kwargs)
        context.update({
            'lastseen_time'   : self.request.session.get('last_seen', None),
            'page'            : int(self.page),
            'FORUM_BASE_NAME' : FORUM_BASE_NAME
        })
        return context


class NewTopics(BaseTopicList):
    """
    Subclasses BaseTopicList to provide new topics.
    New topics are whatever is new since the visitor was last seen,
    or from the past day, whichever is greater.
    """

    def get_queryset(self):
        one_day_ago = datetime.now() - timedelta(days=1)
        one_day_ago_int = time.mktime(one_day_ago.timetuple())
        last_seen_timestamp = self.request.session.get('last_seen_timestamp', None)
        if not last_seen_timestamp or last_seen_timestamp > one_day_ago_int:
            last_seen_timestamp = one_day_ago_int
        return Topic.objects.filter(modified_int__gt=last_seen_timestamp).select_related('post')

    def get_context_data(self, **kwargs):
        context = super(NewTopics, self).get_context_data(**kwargs)
        context.update({
            'forum_slug' : 'latest-topics',
            'forum_name' : "Latest active topics",
        })
        return context
new_topics = NewTopics.as_view()


class TopicList(BaseTopicList):
    """
    Subclasses BaseTopicList to provide topics for a given forum.
    Expects that forum_slug was passed to (and picked up by) BaseTopicList.
    """
    def get_queryset(self):
        self.forum = get_object_or_404(Forum, slug=self.forum_slug)
        return self.forum.topic_set.order_by('-is_sticky', '-modified_int')

    def get_context_data(self, **kwargs):
        context = super(TopicList, self).get_context_data(**kwargs)
        context.update({
            'forum_slug'   : self.forum_slug,
            'forum_name'   : self.forum.name,
            'admin_msg'    : self.forum.message,
            'can_add_topic': True
        })
        return context
topic_list = TopicList.as_view()


class PostList(ListView):
    """
    Returns a paginated list of posts within a topic.
    If it's an ajax request (request has key xhr) it will append the post list.
    Otherwise, it goes to the post wrapper.
    """
    template_name = 'fretboard/post_wrapper.html'
    paginate_by = PAGINATE_BY
    context_object_name = 'posts'

    def dispatch(self, request, *args, **kwargs):
        self.topic = get_object_or_404(Topic, id=kwargs.get('t_id'))
        self.page  = kwargs.get('page', 1)

        # if topic has a redirect, just go there
        if self.topic.redirect_url:
            return redirect(self.topic.redirect_url)
        # if this is an ajax request, use the template snippet
        if request.is_ajax():
            self.template_name = 'fretboard/includes/post_list.html'
        return super(PostList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Post.objects.filter(topic__id=self.kwargs.get('t_id'))

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        forum   = self.topic.forum
        # start number tells the numbered lists where to start counting.
        start_number = int(self.page)
        newposts     = None
        new_post_id  = None

        if start_number > 1:
            start_number = (PAGINATE_BY * (start_number - 1)) + 1

        if 'last_seen' in self.request.session:
            newposts = self.get_queryset().filter(post_date__gt=self.request.session['last_seen']).values_list('id', flat=True)
            try:
                new_post_id = newposts[0]
            except IndexError:
                pass

        canonical_url = "%spage%s/" % (self.topic.get_short_url(), self.page)

        context.update({
            'locked'        : self.topic.is_locked,
            'topic'         : self.topic,
            'topic_id'      : self.topic.id,
            'topic_slug'    : self.topic.slug,
            'start_number'  : start_number,
            'newposts'      : newposts,
            'new_post_id'   : new_post_id,
            'page'          : self.page,
            'forum_slug'    : forum.slug,
            'forum_name'    : forum.name,
            'canonical_url' : canonical_url,
            'form'          : PostForm(),
        })
        return context
post_list = PostList.as_view()

class ForumSearch(BaseTopicList):
    forum_name = 'Forum search'

    def dispatch(self, request, *args, **kwargs):
        self.topicfilter = TopicFilter(request.GET)
        self.postfilter  = PostFilter(request.GET)
        return super(ForumSearch, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.name_search = request.GET.get('name', '')
        self.text_search = request.GET.get('text', '')
        # If we have no parameters, just show the search.
        if self.name_search == '' and self.text_search == '':
            return render(request, self.template_name, {
                'filter': self.topicfilter,
                'postfilter': self.postfilter,
            })
        self.object_list = self.get_queryset()
        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)

    def get_queryset(self):
        if self.name_search != '':
            return self.topicfilter.qs
        # if it's a post search, override the default topic list template.
        self.template_name = 'fretboard/filter_results.html'
        return self.postfilter.qs

    def get_context_data(self, **kwargs):
        context = super(ForumSearch, self).get_context_data(**kwargs)
        if self.name_search != '':
            search_type = 'Topic'
            query = self.name_search
        else:
            search_type = 'Post'
            query = self.text_search
        context.update({
            'search_type': search_type,
            'forum_slug': 'search',
            'forum_name': self.forum_name,
            'query': query,
            'filter': self.topicfilter,
            'postfilter': self.postfilter,
            'page': self.page,
        })
        return context
forum_search = ForumSearch.as_view()
