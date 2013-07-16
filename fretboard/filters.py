import django_filters

from fretboard.models import Topic, Post


class TopicFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    queryset = Topic.objects.filter(is_locked=False)

    class Meta:
        model = Topic
        fields = ['name']


class PostFilter(django_filters.FilterSet):
    text = django_filters.CharFilter(lookup_type='icontains')
    queryset = Post.objects.all().order_by('-id')

    class Meta:
        model = Post
        fields = ['text']
