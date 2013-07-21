from django import forms
from django.conf import settings

from .models import Topic, Post

placeholder = getattr(settings, "FORUM_POST_PLACEHOLDER", "Be nice.")


class AddTopicForm(forms.ModelForm):
    """
    Form for adding a new topic.
    """
    text  = forms.CharField(widget=forms.Textarea(attrs={'tabindex': '2', 'placeholder': placeholder}))
    image = forms.CharField(widget=forms.FileInput(), required=False)

    class Meta:
        model = Topic
        fields = ['name', 'image', 'text']
        widgets = {
            'forum': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(AddTopicForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'tabindex': '1'}


class PostForm(forms.ModelForm):
    """
    Form for adding or editing a post.
    """
    class Meta:
        model = Post
        fields = ['image', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'tabindex': '1', 'placeholder': placeholder}),
            'topic': forms.HiddenInput(),
            'topic_page': forms.HiddenInput(),
            'author': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = ""
