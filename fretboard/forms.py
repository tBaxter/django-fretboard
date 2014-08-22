from django import forms

from .models import Topic, Post
from .settings import COMMENT_PLACEHOLDER



class AddTopicForm(forms.ModelForm):
    """
    Form for adding a new topic.
    """
    text  = forms.CharField(widget=forms.Textarea(attrs={'tabindex': '2', 'placeholder': COMMENT_PLACEHOLDER}))
    image = forms.CharField(widget=forms.FileInput(), required=False)

    class Meta:
        model = Topic
        fields = ['forum', 'name', 'image', 'text']
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
            'text': forms.Textarea(attrs={'tabindex': '1', 'placeholder': COMMENT_PLACEHOLDER}),
            'topic': forms.HiddenInput(),
            'user': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = ""
