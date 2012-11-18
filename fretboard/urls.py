from django.conf.urls.defaults import *
from django.views.generic import ListView

from fretboard.models import Forum
from fretboard.views import *


urlpatterns = patterns('fretboard.views.moderate',
  (r'^close_topic/(?P<topic_id>[0-9]+)/(?P<forum_slug>[-\w]+)/$',   'close_topic'),
  (r'^open_topic/(?P<topic_id>[0-9]+)/(?P<forum_slug>[-\w]+)/$',    'open_topic'),
  (r'^move_topic/(?P<topic_id>[0-9]+)/(?P<forum_slug>[-\w]+)/$',    'move_topic'),
  (r'^delete_topic/(?P<topic_id>[0-9]+)/(?P<forum_slug>[-\w]+)/$',  'delete_topic'),
  (r'^delete_post/(?P<post_id>[0-9]+)/(?P<topic_id>[0-9]+)/$',      'delete_post'),
  (r'^stick_topic/(?P<topic_id>[0-9]+)/(?P<forum_slug>[-\w]+)/$',   'stick_topic'),
  (r'^unstick_topic/(?P<topic_id>[0-9]+)/(?P<forum_slug>[-\w]+)/$', 'unstick_topic'),
)

urlpatterns += patterns('',
  url(r'^new-topics/$',                            SinceLastVisit.as_view(), name="new_last_visit"),
  url(r'^new-topics/page(?P<page>[0-9]+)/$',       SinceLastVisit.as_view(), name="new_last_visit_paginated"),
  url(r'^recently-viewed/$',                       RecentlyViewed.as_view(), name="recently_viewed"),
  url(r'^recently-viewed/page(?P<page>[0-9]+)/$',  RecentlyViewed.as_view(), name="recently_viewed_paginated"),
  url(r'^my-topics/$',                             MemberTopics.as_view(),   name="member_topics"),
  url(r'^my-topics/page(?P<page>[0-9]+)/$',        MemberTopics.as_view(),   name="member_topics_paginated"),
)

urlpatterns += patterns('fretboard.views.crud',
  url(r'^(?P<forum_slug>[-\w]+)/add-topic/$',                              'add_topic', name="add_topic"),
  url(r'^add_post/(?P<t_slug>[-\w]+)/(?P<t_id>[0-9]+)/$',                  'add_post',  name="add_post"),
  url(r'^add_post/(?P<t_slug>[-\w]+)/(?P<t_id>[0-9]+)/(?P<p_id>[0-9]+)/$', 'add_post',  name="add_post_with_quote"),
  url(r'^edit_post/(?P<post_id>[0-9]+)/$',                                 'edit_post', name="edit_post"),
)

urlpatterns += patterns('',
  url(r'^search/$',                                      filter_search, name='fretboard_search'),
  url(r'^latest-topics/$',                               LatestTopics.as_view(), name="new_24_hours"),
  url(r'^latest-topics/page(?P<page>[0-9]+)/$',          LatestTopics.as_view(), name="new_24_hours_paginated"),
  url(r'^(?P<forum_slug>[-\w]+)/$',                      TopicList.as_view(),    name="topic_list"),
  url(r'^(?P<forum_slug>[-\w]+)/page(?P<page>[0-9]+)/$', TopicList.as_view(),    name="topic_list_paginated"),
  url(r'^(?P<f_slug>[-\w]+)/(?P<t_slug>[-\w]+)/(?P<t_id>[0-9]+)/page(?P<page>[0-9]+)/$', PostList.as_view(), name="post_list_paginated"),
  url(r'^(?P<f_slug>[-\w]+)/(?P<t_slug>[-\w]+)/(?P<t_id>[0-9]+)/$', PostList.as_view(), name="post_short_url"),
)
urlpatterns += patterns('',
  # Forum index
  url(r'^$', ListView.as_view(
    queryset=Forum.objects.all().order_by('category'),
    context_object_name="forums",
    template_name="fretboard/category_list.html"
  ), name='fretboard_index'),
)
