from django import forms

from .models import Topic, Post
class AddTopicForm(forms.ModelForm):
	name  = forms.CharField(widget=forms.TextInput(attrs={'tabindex':'1', 'placeholder':"Topic name"}))
	text  = forms.CharField(widget=forms.Textarea(attrs={'tabindex':'2'}))
	
	class Meta:
		model = Topic

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
