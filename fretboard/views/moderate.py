from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from fretboard.models import Forum, Topic, Post

pag_by     = settings.PAGINATE_BY


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


def move_topic(request, topic_id, forum_slug):
    """
    Move topic. If we know the destination, just do it. Otherwise, provide a page to make the selection.
    """
    if request.user.is_staff:
        if request.POST and len(request.POST['forum']) > 0:
            topic = Topic.objects.get(id=topic_id)
            topic.forum = Forum.objects.get(id=request.POST['forum'])
            topic.save()
        else:
            forums = Forum.objects.exclude(slug=forum_slug)
            topic = Topic.objects.get(id=topic_id)
            return render(request, 'fretboard/utils/move_topic.html', {'forums': forums, 'topic': topic})
    else:
        messages.error(request, "You don't have permissions to move topics.")
    return HttpResponseRedirect("/forum/{0}/".format(forum_slug))





def delete_topic(request, topic_id, forum_slug):
    """ Deletes a topic and all related posts """
    if not request.user.is_staff:
        messages.error(request, "You can't do that!")
        return HttpResponseRedirect("/forum/" + str(forum_slug) + "/")
    Post.objects.filter(topic__id=topic_id).delete()
    Topic.objects.get(id=topic_id).delete()
    return HttpResponseRedirect("/forum/" + str(forum_slug) + "/")


# stick/unstick topic
def stick_topic(request, topic_id, forum_slug):
        if request.user.is_staff:
                topic = Topic.objects.get(id=topic_id)
                topic.is_sticky=True
                topic.save()
                return HttpResponseRedirect("/forum/" + forum_slug +"/")
        else:
                raise Http404

def unstick_topic(request, topic_id, forum_slug):
        if request.user.is_staff:
                topic = Topic.objects.get(id=topic_id)
                topic.is_sticky=False
                topic.save()
        return HttpResponseRedirect("/forum/" + forum_slug +"/")
        

# delete a post
def delete_post(request, post_id, topic_id):
    post = Post.objects.get(id=post_id)
    if request.user.is_authenticated() and (request.user.is_staff or request.user.id == post.author.id):
        topic = Topic.objects.get(id=topic_id)
        post.delete()
        topic_posts = topic.post_set.count()
        #if topic_posts == 0:
        #    topic.delete()
        #    return HttpResponseRedirect("/forum/" + str(topic.forum.slug) +  "/")
        pmax = (topic_posts/pag_by)+1
        return HttpResponseRedirect("/forum/" + str(topic.forum.slug) +  "/" + str(topic.slug) + "/" + topic_id + "/page"+ str(pmax) + "/")
    else:
        raise Http404

