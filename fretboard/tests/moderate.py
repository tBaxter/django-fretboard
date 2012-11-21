from django.core.urlresolvers import reverse
from django.test import TestCase

from fretboard.models import Forum, Topic


class TestFretboardModerationViews(TestCase):
    """
    Tests for moderation views.
    """
    fixtures = ['fretboard_test_data.json']

    def setUp(self):
        self.forum    = Forum.objects.get(id=1)
        self.topic    = Topic.objects.get(id=1)


def test_topic_move(self):
    """
    Testing moving forum topic.
    """
    # if this is a GET request, we should get bounced back to move topic form.
    resp = self.client.get(reverse('move_topic', args=[
        self.topic.id,
        self.forum.slug
    ]))
    self.assertEqual(resp.status_code, 200)
