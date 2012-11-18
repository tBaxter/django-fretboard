from fretboard.models import Topic, Post

import django_filters

class TopicFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(lookup_type='icontains')
	class Meta:
		model = Topic
		fields = ['name']

class PostFilter(django_filters.FilterSet):
	text = django_filters.CharFilter(lookup_type='icontains')
	class Meta:
		model = Post
		fields = ['text']