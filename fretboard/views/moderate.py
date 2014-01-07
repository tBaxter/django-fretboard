from django.contrib import messages
from django.shortcuts import render, redirect

from fretboard.models import Forum, Topic, Post


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
    return redirect("/forum/{0}/".format(forum_slug))
