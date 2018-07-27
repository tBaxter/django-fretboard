from django.urls import path

from .views import moderate, \
  member_topics, commented_topics, recently_viewed, \
  add_topic, add_post, edit_post, delete_post, \
  topic_list, post_list, category_list, \
  forum_search, new_topics


urlpatterns = [
  path(
    'moderation/<int:topic_id>/<slug:forum_slug>/',
    moderate,
    name='mod_topic'
  ),
  # member urls
  path('my-topics/', member_topics, name="member_topics"),
  path('member-topics/<slug:user>/', member_topics, name="topics_for_user"),
  path('my-commented-topics', commented_topics, name="commented_topics"),
  path('recently-viewed', recently_viewed, name="recently_viewed"),

  # CRUD
  path('add-topic/', add_topic, name="generic_add_topic"),
  path('<slug:forum_slug>/add-topic/', add_topic, name="add_topic"),
  path(
    'add_post/<slug:slug:t_slug>/<int:int:t_id>/',
    add_post,
    name="add_post"
  ),
  path(
    'add_post/<slug:slug:t_slug>/<int:int:t_id>/<int:p_id>/',
    add_post,
    name="post_with_quote"
  ),
  path('edit_post/<int:posint:t_id>/', edit_post, name="edit_post"),
  path(
    'delete_post/<int:posint:t_id>/<int:topic_id>/',
    delete_post,
    name='delete_post'
  ),

  path('search/', forum_search, name='fretboard_search'),
  path('new-topics/', new_topics, name="new_topics"),
  path('new-topics/page<int:page>/', new_topics, name="new_topics_paginated"),
  path('latest-topics/', new_topics, name="new_24_hours"),
  path('latest-topics/page<int:page>/', new_topics, name="new_24_hours_paginated"),
  # topic lists
  path('<slug:forum_slug>/', topic_list, name="topic_list"),
  path('<slug:forum_slug>/page<int:page>/', topic_list, name="topic_list_paginated"),
  # post lists
  path(
    '<slug:f_slug>/<slug:t_slug>/<int:t_id>/page<int:page>/',
    post_list,
    name="post_list_paginated"
  ),
  path(
    '<slug:f_slug>/<slug:t_slug>/<int:t_id>/',
    post_list,
    name="post_short_url"
  ),
  path('', category_list, name='fretboard_index'),
]
