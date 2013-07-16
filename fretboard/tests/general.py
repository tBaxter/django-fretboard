from django.core.urlresolvers import reverse
from django.test import TestCase

from fretboard.models import Forum, Topic


class TestFretboardGeneralViews(TestCase):
    fixtures = ['fretboard_test_data.json']

    def setUp(self):
        self.forum    = Forum.objects.get(id=1)
        self.topic    = Topic.objects.get(id=1)

    def test_index(self):
        """
        Test index (category list)
        """
        resp = self.client.get(reverse('fretboard_index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('forums' in resp.context)

    def test_topic_list(self):
        """
        Test general, category-based topic list.
        """
        resp = self.client.get(reverse('topic_list', args=[self.forum.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)
        self.assertTrue('page' in resp.context)
        self.assertTrue('lastseen_time' in resp.context)

    def test_latest_topics(self):
        """
        Test of latest topics list.
        """
        resp = self.client.get(reverse('new_24_hours'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)
        self.assertTrue('page' in resp.context)

    def test_post_list(self):
        """
        Test for validiity of topic post list.
        """
        resp = self.client.get(reverse('post_short_url', args=[self.forum.slug, self.topic.slug, self.topic.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)
        self.assertTrue('locked' in resp.context)
        self.assertTrue('topic' in resp.context)
        self.assertTrue('topic_id' in resp.context)
        self.assertTrue('topic_slug' in resp.context)
        self.assertTrue('start_number' in resp.context)
        self.assertTrue('page' in resp.context)
        self.assertTrue('forum_slug' in resp.context)
        self.assertTrue('forum_name' in resp.context)
        self.assertTrue('form' in resp.context)

    def test_topic_search(self):
        """
        Tests that topic names are searched.
        """
        resp = self.client.get(reverse('fretboard_search') + '?name=test&text')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)
        self.assertTrue('query' in resp.context)

    def test_post_search(self):
        """
        Test that post text is searched.
        """
        resp = self.client.get(reverse('fretboard_search') + '?name&text=test')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)
        self.assertTrue('query' in resp.context)
