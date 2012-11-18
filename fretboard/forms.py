from django import forms
from fretboard.models import Topic, Post

# add topic
class AddTopicForm(forms.ModelForm):
	name  = forms.CharField(widget=forms.TextInput(attrs={'tabindex':'1', 'placeholder':"Topic name"}))
	text  = forms.CharField(widget=forms.Textarea(attrs={'tabindex':'2'}))
	
	class Meta:
		model = Topic
		
		
		
# add post
class PostForm(forms.ModelForm):
	class Meta:
		model = Post