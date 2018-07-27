import unittest

from django.urls import reverse
from django.test import TestCase

from .models import Forum, Topic


class TestFretboardCrudViews(TestCase):
    """
    Tests for Creation, Update and Deletion views.
    """
    fixtures = ['fretboard_test_data.json', 'auth_users.json']

    def setUp(self):
        self.forum = Forum.objects.get(id=1)
        self.topic = Topic.objects.get(id=1)

    @unittest.skip("Template is overly opinionated")
    def test_topic_addition(self):
        """
        Testing creating a new forum topic.
        """
        post_data = {
            'name': "This is a new topic.",
            'text': "This is a new topic that was created via the testing suite."
        }
        current_topic_count = self.forum.topic_set.count()
        # if this is a GET request, we should get bounced back
        # to the form without creating a new post.
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


class TestFretboardGeneralViews(TestCase):
    fixtures = ['fretboard_test_data.json', 'auth_users.json']

    def setUp(self):
        self.forum = Forum.objects.get(id=1)
        self.topic = Topic.objects.get(id=1)

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

    @unittest.skip("Template is overly opinionated")
    def test_latest_topics(self):
        """
        Test of latest topics list.
        """
        resp = self.client.get(reverse('new_24_hours'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)
        self.assertTrue('page' in resp.context)

    @unittest.skip("Template is overly opinionated")
    def test_post_list(self):
        """
        Test for validiity of topic post list.
        """
        resp = self.client.get(
            reverse('post_short_url', args=[self.forum.slug, self.topic.slug, self.topic.id])
        )
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

    @unittest.skip("Template is overly opinionated")
    def test_topic_search(self):
        """
        Tests that topic names are searched.
        """
        resp = self.client.get(reverse('fretboard_search') + '?name=test&text')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)
        self.assertTrue('query' in resp.context)

    @unittest.skip("Template is overly opinionated")
    def test_post_search(self):
        """
        Test that post text is searched.
        """
        resp = self.client.get(reverse('fretboard_search') + '?name&text=test')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)
        self.assertTrue('query' in resp.context)


class TestFretboardModerationViews(TestCase):
    """
    Tests for moderation views.
    """
    fixtures = ['fretboard_test_data.json', 'auth_users.json']

    def setUp(self):
        self.forum = Forum.objects.get(id=1)
        self.topic = Topic.objects.get(id=1)

    @unittest.skip("Template is overly opinionated")
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
