# Create, Remove, Update, Delete views

import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags

from fretboard.forms import AddTopicForm, PostForm
from fretboard.helpers import update_post_relations
from fretboard.models import Forum, Topic, Post
from fretboard.settings import PAGINATE_BY, FORUM_BASE_NAME


@login_required
def add_topic(request, forum_slug=None):
    """ Adds a topic to a given forum """
    forum = Forum.objects.get(slug=forum_slug)
    form  = AddTopicForm(request.POST or None, request.FILES or None, initial={'forum': forum})

    current_time   = time.time()
    user           = request.user

    if form.is_valid():
        instance = form.save(commit=False)
        instance.forum           = forum
        instance.name            = strip_tags(instance.name)
        instance.slug            = slugify(instance.name)
        instance.user            = user
        instance.author          = user.display_name
        instance.lastpost_author = user.display_name
        instance.created_int     = current_time
        instance.modified_int    = current_time
        instance.save()

        # and now add the child post
        post = Post(
            topic            = instance,
            text             = request.POST['text'],
            user             = user,
            post_date_int    = current_time
        )
        if request.FILES:
            post.image = request.FILES['image']
        post.save()

        return HttpResponseRedirect("/forum/%s/?new_topic=%s" % (forum_slug, instance.id))

    return render(request, 'fretboard/add_edit.html', {
        'form': form,
        'form_title': 'Add a topic',
        'FORUM_BASE_NAME': FORUM_BASE_NAME
    })


@login_required
def add_post(request, t_slug, t_id, p_id = False):  # topic slug, topic id, post id
    """
    Creates a new post and attaches it to a topic
    """
    topic     = get_object_or_404(Topic, id=t_id)
    topic_url = '{0}page{1}/'.format(topic.get_short_url(), topic.page_count)
    user      = request.user
    current_time = time.time()
    form_title = 'Add a post'

    if topic.is_locked:  # If we mistakenly allowed reply on locked topic, bail with error msg.
        messages.error(request, 'Sorry, but this topic is closed')
        return HttpResponseRedirect(topic_url)

    q = None
    if p_id:  # if there's a post id, it's a quote
        q = Post.objects.get(id=p_id)
        form_title = "Respond to post"

    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        # we're going to save this inital data now,
        # rather than on the model save()
        # because we only want to bother with this stuff one time
        # and it will never update or change.

        instance = form.save(commit=False)
        instance.topic  = topic
        instance.user = user
        instance.author_name = user.display_name
        instance.avatar = user.avatar
        instance.post_date_int = current_time
        instance.quote = q
        instance.save()

        update_post_relations(user, topic)

        return HttpResponseRedirect('%s?new_post=%s#post-%s' % (topic_url, t_id, instance.id))
    return render(request, 'fretboard/add_edit.html', {
        'form': form,
        'form_title': form_title,
        'quote': q,
        'FORUM_BASE_NAME': FORUM_BASE_NAME
    })


@login_required
def edit_post(request, post_id):
    """
    Allows user to edit an existing post.
    This needs to be rewritten. Badly.
    """
    post   = get_object_or_404(Post, id=post_id)
    user   = request.user

    topic  = post.topic
    # oughta build a get_absolute_url method for this, maybe.
    post_url = '{0}page{1}/#post{2}'.format(topic.get_short_url(), topic.page_count, post.id)

    if topic.is_locked:
        messages.error(request, 'Sorry, but this topic is closed')
        return HttpResponseRedirect(post_url)

    if user.is_staff is False and user.id != post.author.id:
        messages.error(request, "Sorry, but you can't edit this post.")
        return HttpResponseRedirect(post_url)

    if request.POST and len(request.POST['text']) > 1:
        if request.is_ajax and 'body' in request.POST:  # AJAX REQUEST
            post.text = request.POST['body']
            post.save(update_fields=['text', 'text_formatted'])
            return HttpResponse(str(post.text))
        post.text = request.POST['text']
        post.save(update_fields=['text', 'text_formatted'])

        if 'name' in request.POST:  # updated topic
            topic.name = request.POST['name']
            topic.save(update_fields=['name'])
        return HttpResponseRedirect(post_url)
    # this is a get request
    else:
        if post == topic.post_set.all()[0]:
            form = AddTopicForm(instance=topic, initial={'text': post.text})
        else:
            form = PostForm(instance=post)
        return render(request, 'fretboard/add_edit.html', {
            'quote': post.quote,
            'form' : form,
            'form_title': 'Edit post',
        })


def delete_post(request, post_id, topic_id):
    """
    Deletes a post, if the user has correct permissions.
    Also updates topic.post_count
    """
    try:
        topic = Topic.objects.get(id=topic_id)
        post = Post.objects.get(id=post_id)
    except:
        messages.error(request, 'Sorry, but this post can not be found. It may have been deleted already.')
        raise Http404
    return_url = "/forum/%s/%s/%s/" % (topic.forum.slug, topic.slug, topic_id)
    if request.user.is_authenticated() and (request.user.is_staff or request.user.id == post.author.id):
        post.delete()
        update_post_relations(request.user, topic, deleting=True)
        topic_posts = topic.post_set.count()
        pmax = (topic_posts / PAGINATE_BY) + 1

        # if no posts are left, delete topic.
        if topic_posts == 0:
            topic.delete()
            return HttpResponseRedirect("/forum/%s/" % topic.forum.slug)

        return HttpResponseRedirect("%spage%s/" % (return_url, pmax))
    else:
        raise Http404
