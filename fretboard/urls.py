from django.urls import path

from .views import moderate, MemberTopics, CommentedTopics, RecentlyViewed, \
  add_topic, add_post, edit_post, delete_post, ForumSearch, NewTopics, \
  TopicList, PostList, CategoryList


urlpatterns = [
  path(
    'moderation/<int:topic_id>/<slug:forum_slug>/',
    moderate,
    name='mod_topic'
  ),
  # member urls
  path('my-topics/', MemberTopics, name="member_topics"),
  path('member-topics/<slug:user>/', MemberTopics, name="topics_for_user"),
  path('my-commented-topics', CommentedTopics, name="commented_topics"),
  path('recently-viewed', RecentlyViewed, name="recently_viewed"),

  # CRUD
  path('add-topic/', add_topic, name="generic_add_topic"),
  path('<slug:forum_slug>/add-topic/', add_topic, name="add_topic"),
  path('add_post/<slug:slug:t_slug>/<int:int:t_id>/', add_post, name="add_post"),
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

  path('search/', ForumSearch, name='fretboard_search'),
  path('new-topics/', NewTopics, name="new_topics"),
  path('new-topics/page<int:page>/', NewTopics, name="new_topics_paginated"),
  path('latest-topics/', NewTopics, name="new_24_hours"),
  path('latest-topics/page<int:page>/', NewTopics, name="new_24_hours_paginated"),
  # topic lists
  path('<slug:forum_slug>/', TopicList, name="topic_list"),
  path('<slug:forum_slug>/page<int:page>/', TopicList, name="topic_list_paginated"),
  # post lists
  path(
    '<slug:f_slug>/<slug:t_slug>/<int:t_id>/page<int:page>/',
    PostList,
    name="post_list_paginated"
  ),
  path(
    '<slug:f_slug>/<slug:t_slug>/<int:t_id>/',
    PostList,
    name="post_short_url"
  ),
  path('', CategoryList, name='fretboard_index'),
]
