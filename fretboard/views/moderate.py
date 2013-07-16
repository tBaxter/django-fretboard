from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from fretboard.models import Forum, Topic, Post

pag_by     = settings.PAGINATE_BY


def moderate(request, topic_id, forum_slug):
    resave_topic = True
    action = request.GET.get('act', None)
    if request.user.is_staff:
        topic = Topic.objects.get(id=topic_id)
        if action == 'lock':
            topic.is_locked = True
        elif action == 'unlock':
            topic.is_locked = False
        elif action == 'delete':
            Post.objects.filter(topic__id=topic_id).delete()
            topic.delete()
            resave_topic = False
        elif action == 'stick':
            topic.is_sticky = True
        elif action == 'unstick':
            topic.is_sticky = False
        elif action == 'move':
            if request.GET.get('forum'):
                topic.forum = Forum.objects.get(id=request.GET['forum'])
            else:
                forums = Forum.objects.exclude(slug=forum_slug)
                return render(request, 'fretboard/utils/move_topic.html', {
                    'forums': forums, 
                    'topic': topic,
                    'act': action
                })
        else:
            messages.error(request, "We didn't recognize the command: %s." % action)
        if resave_topic:
            topic.save()
    else:
        if not action:
            messages.error(request, "We couldn't find an action: %s" % action)
        else:
            messages.error(request, "You don't have permission to %s topics." % action)
    return HttpResponseRedirect("/forum/{0}/".format(forum_slug))

"""
# close topic
def close_topic(request, topic_id, forum_slug):
    if request.user.is_staff:
        topic = Topic.objects.get(id=topic_id)
        topic.is_locked = True
        topic.save()
    else:
        messages.error(request, "You don't have permission to close topics.")
    return HttpResponseRedirect("/forum/{0}/".format(forum_slug))


def open_topic(request, topic_id, forum_slug):
    """ Reopens locked topic. """
    redirect_to = "/forum/{0}/".format(forum_slug)
    if request.user.is_authenticated():
        user_data = User.objects.get(username=str(request.user))
        if user_data.is_staff:
            topic = Topic.objects.get(id=topic_id)
            topic.is_locked = False
            topic.save()
            return HttpResponseRedirect(redirect_to)
        else:
            messages.error(request, "You can't unlock topics. You aren't a moderator.")
            return HttpResponseRedirect(redirect_to)
    else:
        messages.error(request, "You can't do that. You aren't a moderator, or you aren't logged in.")
        return HttpResponseRedirect(redirect_to)


def move_topic(request, t_id, f_slug):
    """
    Move topic. If we know the destination, just do it. Otherwise, provide a page to make the selection.
    """
    if request.user.is_staff:
        if request.POST and len(request.POST['forum']) > 0:
            topic = Topic.objects.get(id=t_id)
            topic.forum = Forum.objects.get(id=request.POST['forum'])
            topic.save()
        else:
            forums = Forum.objects.exclude(slug=f_slug)
            topic = Topic.objects.get(id=t_id)
            return render(request, 'fretboard/utils/move_topic.html', {'forums': forums, 'topic': topic})
    else:
        messages.error(request, "You don't have permissions to move topics.")
    return HttpResponseRedirect("/forum/{0}/".format(f_slug))





def delete_topic(request, topic_id, forum_slug):
    # Deletes a topic and all related posts
    return_url = "/forum/%s/" % forum_slug
    if request.user.is_staff:
        Post.objects.filter(topic__id=topic_id).delete()
        Topic.objects.get(id=topic_id).delete()
    else:
        messages.error(request, "You don't have permissions to delete a topic.")
    return HttpResponseRedirect(return_url)


# stick/unstick topic
def stick_topic(request, topic_id, forum_slug):
    if request.user.is_staff:
        topic = Topic.objects.get(id=topic_id)
        topic.is_sticky = True
        topic.save()
        return HttpResponseRedirect("/forum/%s/" % forum_slug)
    else:
        raise Http404


def unstick_topic(request, topic_id, forum_slug):
    if request.user.is_staff:
        topic = Topic.objects.get(id=topic_id)
        topic.is_sticky = False
        topic.save()
    return HttpResponseRedirect("/forum/%s/" % forum_slug)
"""
