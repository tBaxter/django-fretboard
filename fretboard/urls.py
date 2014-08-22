from django.conf.urls import *

from .views import *


urlpatterns = patterns('fretboard.views.moderate',
  url(
    regex=r'^moderation/(?P<topic_id>[0-9]+)/(?P<forum_slug>[-\w]+)/$',
    view='moderate',
    name='mod_topic'),
)

### URLS for User
urlpatterns += patterns('',
  url(
    name="member_topics",
    regex=r'^my-topics/$',
    view=MemberTopics.as_view()
  ),
  url(
    name="topics_for_user",
    regex=r'^member-topics/(?P<user>[-\w]+)/$',
    view=MemberTopics.as_view()
  ),
  url(
    name="commented_topics",
    regex=r'^my-commented-topics/$',
    view=CommentedTopics.as_view(),
  ),
  url(
    name="recently_viewed",
    regex=r'^recently-viewed/$',
    view=RecentlyViewed.as_view()
  ),
)

### CRUD Urls
urlpatterns += patterns('fretboard.views.crud',
  url(
    r'^add-topic/$',
    'add_topic',
    name="generic_add_topic"
  ),
  url(
    r'^(?P<forum_slug>[-\w]+)/add-topic/$',
    'add_topic',
    name="add_topic"
  ),
  url(
    regex=r'^add_post/(?P<t_slug>[-\w]+)/(?P<t_id>[0-9]+)/$',
    view='add_post',
    name="add_post"
  ),
  url(
    regex=r'^add_post/(?P<t_slug>[-\w]+)/(?P<t_id>[0-9]+)/(?P<p_id>[0-9]+)/$',
    view='add_post',
    name="post_with_quote"
  ),
  url(
    regex=r'^edit_post/(?P<post_id>[0-9]+)/$',
    view='edit_post',
    name="edit_post"
  ),
  url(
    regex=r'^delete_post/(?P<post_id>[0-9]+)/(?P<topic_id>[0-9]+)/$',
    view='delete_post',
    name='delete_post'
  ),
)

urlpatterns += patterns('',
  url(
    r'^search/$',
    ForumSearch.as_view(),
    name='fretboard_search'
  ),
  url(
    regex=r'^new-topics/$',
    view=NewTopics.as_view(),
    name="new_topics"
  ),
  url(
    regex=r'^new-topics/page(?P<page>[0-9]+)/$',
    view=NewTopics.as_view(),
    name="new_topics_paginated"),

  url(
    regex=r'^latest-topics/$',
    view=NewTopics.as_view(),
    name="new_24_hours"
  ),
  url(
    regex=r'^latest-topics/page(?P<page>[0-9]+)/$',
    view=NewTopics.as_view(),
    name="new_24_hours_paginated"
  ),
  # topic lists
  url(
    regex=r'^(?P<forum_slug>[-\w]+)/$',
    view=TopicList.as_view(),
    name="topic_list"
  ),
  url(
    regex=r'^(?P<forum_slug>[-\w]+)/page(?P<page>[0-9]+)/$',
    view=TopicList.as_view(),
    name="topic_list_paginated"
  ),
  # post lists
  url(
    regex=r'^(?P<f_slug>[-\w]+)/(?P<t_slug>[-\w]+)/(?P<t_id>[0-9]+)/page(?P<page>[0-9]+)/$',
    view=PostList.as_view(),
    name="post_list_paginated"
  ),
  url(
    regex=r'^(?P<f_slug>[-\w]+)/(?P<t_slug>[-\w]+)/(?P<t_id>[0-9]+)/$',
    view=PostList.as_view(),
    name="post_short_url"
  ),
  # category list/index
  url(
    regex=r'^$',
    view=CategoryList.as_view(),
    name='fretboard_index'
  ),
)
