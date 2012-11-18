from django.core.urlresolvers import reverse
from django.test import TestCase

from fretboard.models import Forum, Topic


class TestFretboardCrudViews(TestCase):
    """
    Tests for Creation, Update and Deletion views.
    """
    fixtures = ['fretboard_test_data.json']

    def setUp(self):
        self.forum    = Forum.objects.get(id=1)
        self.topic    = Topic.objects.get(id=1)


def test_topic_addition(self):
    """
    Testing creating a new forum topic.
    """
    post_data = {
        'name': "This is a new topic.",
        'text': "This is a new topic that was created via the testing suite."
    }
    current_topic_count = self.forum.topic_set.count()
    # if this is a GET request, we should get bounced back to the form without creating a new post.
    resp = self.client.get(reverse('add_topic', args=[self.forum.slug]), post_data)
    self.assertEqual(resp.status_code, 302)
    self.assertEqual(resp['Location'], reverse('add_topic', args=[self.forum.slug]))
    self.assertEqual(self.forum.topic_set.count(), current_topic_count)

    # If it's a post, we should see a new topic created.
    # If the form was validated, the response status code should be 302,
    # and it should bounce to the parent forum.
    resp = self.client.post(reverse('add_topic', args=[self.forum.slug]), post_data)
    self.assertEqual(resp.status_code, 302)
    self.assertEqual(resp['Location'], reverse('topic_list', args=[self.forum.slug]))
    self.assertTrue(self.forum.topic_set.count() > current_topic_count)
