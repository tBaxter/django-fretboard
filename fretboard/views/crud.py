# Create, Remove, Update, Delete views

import datetime
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags

from fretboard.forms import AddTopicForm, PostForm
from fretboard.helpers import clean_text, format_post
from fretboard.models import Forum, Topic, Post
from fretboard.signals import forum_post_saved

now        = datetime.datetime.now()
pag_by     = settings.PAGINATE_BY
mobile     = ''


@login_required
def add_topic(request, forum_slug):
    """ Adds a topic to forum """
    form = AddTopicForm()
    if not request.POST:
        return render(request, 'fretboard/add_edit.html', {
          'form': form,
          'add_topic': 'True',
          'user': request.user,
          'formtype': 'Add a topic'
        })
    else:
        data                      = request.POST.copy()
        forum                     = Forum.objects.get(slug=forum_slug)
        user                      = request.user
        topic_name                = strip_tags(data['name'])
        cleaned                   = clean_text(data['text'])
        formatted                 = format_post(cleaned)
        created                   = time.time()

        data['forum']             = forum.id
        data['name']              = topic_name
        data['slug']              = slugify(topic_name)
        data['author']            = user.preferred_name
        data['lastpost_author']   = user.preferred_name
        data['page_count']        = 1
        data['post_count']        = 1
        data['created_int']       = created
        data['modified_int']      = created

        form = AddTopicForm(data, request.FILES)
        if form.is_valid():
            new_topic = form.save()
            post = Post(
                topic            = new_topic,
                text             = cleaned,
                text_formatted   = formatted,
                author           = user,
                author_name      = user.preferred_name,
                topic_page       = 1,
                avatar           = user.avatar,
                post_date_int    = created
            )
            if request.FILES:
                post.image     = request.FILES['image']
            post.save()
            # update related
            forum_post_saved.send(sender=None, request=request, site_user=user, post=post, topic=new_topic)
            return HttpResponseRedirect("/forum/%s/?new_topic=%s" % (forum_slug, new_topic.id))
        return render(request, 'fretboard/add_edit.html', {'form': form, 'add_topic': 'True', 'user': user, 'formtype': 'Add a topic'})


@login_required
def add_post(request, t_slug, t_id, p_id = False, mobile=""):  # topic slug, topic id, post id
    """
    Creates a new post and attaches it to a topic
    """
    topic     = Topic.objects.get(id=t_id)
    topic_url = '{0}page{1}/'.format(topic.get_short_url(), topic.page_count)
    user      = request.user

    if topic.is_locked:  # If we mistakenly allowed reply on locked topic, bail with error msg.
        messages.error(request, 'Sorry, but this topic is closed')
        return HttpResponseRedirect(topic_url)
    form = PostForm()
    q = None
    if p_id:  # if there's a post id, it's a quote
        q = Post.objects.get(id=p_id)
        quote_text = """<blockquote cite="%s#%s">%s\n\n<footer>&ndash; %s</footer>\n</blockquote>\n\n""" % (q.topic_page, q.id, q.text_formatted, q.author_name)

    if request.POST:
        data                   = request.POST.copy()
        cleaned                = clean_text(data['text'])
        data['topic']          = topic.id
        data['author']         = user.id
        data['author_name']    = user.preferred_name
        data['text']           = cleaned
        data['text_formatted'] = format_post(cleaned)
        data['avatar']         = user.avatar
        data['votes']          = 0

        if q:
            data['quote']          = q.id
            data['text_formatted'] = quote_text + data['text_formatted']

        if topic.post_set.count() % pag_by == 0:
            data['topic_page'] = topic.page_count + 1
        else:
            data['topic_page'] = topic.page_count

        form = PostForm(data, request.FILES)
        if form.is_valid():
            new_post = form.save()
            new_post.post_date_int = time.time()
            new_post.save()

            # update related -- # we can't do this via signal. too slow to update before cache
            # check on django 1.5+ update certain fields on model.
            user.post_count += 1
            user.save(update_fields=['post_count'])

            topic.modified     = now
            topic.modified_int = time.time()
            topic.save(update_fields=['modified', 'modified_int'])
            #topic.save()

            if 'mobile' in request.GET:
                mobile = '_!m'
            return HttpResponseRedirect('%s?new_post=%s#post%s%s' % (topic_url, t_id, new_post.id, mobile))
    return render(request, 'fretboard/add_edit.html', {
      'form': form,
      'user': user,
      'formtype': 'Add a post',
      'quote': [q, ],
    })


@login_required
def edit_post(request, post_id, xhr=""):
    """
    Allows user to edit an existing post
    """
    user   = request.user
    post   = Post.objects.get(id=post_id)
    topic  = post.topic
    # oughta build a get_absolute_url method for this, maybe.
    post_url = '{0}/page{1}/#post{2}'.format(topic.get_short_url(), topic.page_count, post.id)
    if topic.is_locked:
        messages.error(request, 'Sorry, but this topic is closed')
        return HttpResponseRedirect(post_url)

    if request.POST and 'body' in request.POST:  # AJAX REQUEST
        post.text = request.POST['body']
        post.save()
        return HttpResponse(str(post.text))

    if user.is_staff or user.id == post.author.id:
        if request.POST and len(request.POST['text']) > 1:
            data                = request.POST.copy()
            post.text           = clean_text(data['text'])
            post.text_formatted = format_post(post.text)
            post.save()
            if 'name' in data:  # updated topic
                topic.name = data['name']
                topic.save(update_fields=['name', ])
            return HttpResponseRedirect(post_url)
        else:  # this is a get request
            form = PostForm()
            return render(request, 'fretboard/add_edit.html', {
               'text' : post.text,
               'quote': [post.quote, ],
               'user' : user,
               'form' : form,
               'topic': topic,
               'formtype': 'Edit post',
             })
    else:  # no permissions
        messages.error(request, "Sorry, but you can't edit this post.")
        return HttpResponseRedirect(post_url)
