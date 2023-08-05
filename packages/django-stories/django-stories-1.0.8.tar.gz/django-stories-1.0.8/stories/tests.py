#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.template import Template, Context
from django.test import TestCase

from stories import settings
from stories.models import Story
from stories.settings import COMMENTS_FROZEN, COMMENTS_DISABLED
from stories.utils import load_widget


def render(src, ctx=None):
    ctx = ctx or {}
    return Template(src).render(Context(ctx))


class BaseTests(TestCase):
    fixtures = ['auth.json', 'profile.json', 'stories.json']

    def setUp(self):
        self.story1 = Story.objects.get(pk=1)
        self.story2 = Story.objects.get(pk=2)


class StoryTests(BaseTests):
    def setUp(self):
        super(StoryTests, self).setUp()

    def test_comments(self):
        self.assertFalse(self.story1.comments_frozen)
        self.story1.comment_status = COMMENTS_DISABLED
        self.story1.save()

        self.assertFalse(self.story1.comments_frozen)

        self.story1.comment_status = COMMENTS_FROZEN
        self.story1.save()

        self.assertTrue(self.story1.comments_frozen)

    def test_author(self):
        self.assertEqual(self.story1.author,
            '<a href="/people/1">John Doe</a> and '\
            '<a href="/people/3">Mark Moe</a>')

    def test_author_display(self):
        ad = self.story1.author_display
        ad = ad.replace('\n', '')
        self.assertEqual(ad,
            '<a href="/users/John/">John Doe</a> and '\
            '<a href="/users/Mark/">Mark Moe</a>')

    def test_paragraphs(self):
        self.assertEqual(len(self.story1.paragraphs), 3)

    def test_published(self):
        # Should be two total stories
        self.assertEqual(len(Story.objects.all()), 2)
        # Only one of these is marked as published
        self.assertEqual(len(Story.published.all()), 1)
        # Mark them all published and make sure they all have a publish_date/time
        unpub = Story.objects.exclude(status=4)[0]
        unpub.publish_date = None
        unpub.publish_time = None
        unpub.save()
        self.assertEqual(unpub.publish_date, None)
        self.assertEqual(unpub.publish_time, None)
        unpub.status = 4
        unpub.save()
        self.assertNotEqual(unpub.publish_date, None)
        self.assertNotEqual(unpub.publish_time, None)
        unpub.status = 1
        unpub.publish_date = None
        unpub.publish_time = None
        unpub.save()

    def test_views(self):
        # Archive views
        self.assertEqual(self.client.get('/news/').status_code, 200)
        self.assertEqual(self.client.get('/news/2012/').status_code, 200)
        self.assertEqual(self.client.get('/news/2012/jul/').status_code, 200)
        self.assertEqual(self.client.get('/news/2012/32/').status_code, 200)
        self.assertEqual(self.client.get('/news/2012/jul/30/').status_code, 200)
        self.assertEqual(self.client.get('/news/today/').status_code, 200)

        # story2 is marked as published, story1 is not
        self.story1.publish_date = None
        self.story1.publish_time = None
        self.assertEqual(self.client.get(
            self.story1.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(
            self.story2.get_absolute_url()).status_code, 200)

        self.assertEqual(self.client.get(
            self.story1.get_absolute_url() + 'print/').status_code, 404)
        self.assertEqual(self.client.get(
            self.story2.get_absolute_url() + 'print/').status_code, 200)
        self.assertEqual(self.client.get(
            self.story1.get_absolute_url() + 'comments/').status_code, 404)
        self.assertEqual(self.client.get(
            self.story2.get_absolute_url() + 'comments/').status_code, 200)

    def test_change_form(self):

        self.assertTrue(self.client.login(username='admin', password='pass'))
        self.assertEqual(
            self.client.get('/admin/stories/story/1/').status_code, 200)

        change_dict = {
            'headline': 'Changed',
            'slug': 'changed',
            'body': "<p>This is the body</p>",
            'status': '1',
            'origin': '0',
            'comment_status': '0',
            'site': '1',
            'publish_date': '2012-03-14',
            'publish_time': '00:00:00'
        }

        cf_post = self.client.post('/admin/stories/story/1/', change_dict)
        self.assertRedirects(cf_post, '/admin/stories/story/')
        self.assertEqual(Story.objects.get(pk=1).headline, 'Changed')

    def test_change_list(self):

        self.assertTrue(self.client.login(username='admin', password='pass'))
        self.assertEqual(
            self.client.get('/admin/stories/').status_code, 200)
        self.assertEqual(
            self.client.get('/admin/stories/story/').status_code, 200)

        change_dict = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MAX_NUM_FORMS': '',
            'action': '',
            'select_across': '0',
            'form-0-id': '1',
            'form-1-id': '2',
            'form-0-status': '3',
            'form-0-headline': 'Changed 1',
            'form-0-subhead': '',
            'form-0-kicker': '',
            'form-0-status': '3',
            'form-0-teaser': '',
            'form-1-status': '3',
            'form-1-headline': 'Changed 2',
            'form-1-subhead' : '',
            'form-1-kicker': '',
            'form-1-status': '3',
            'form-1-teaser': '',
            '_save': 'Save',
        }

        cl_post = self.client.post('/admin/stories/story/', change_dict)
        self.assertRedirects(cl_post, '/admin/stories/story/')
        self.assertEqual(Story.objects.get(pk=1).headline, 'Changed 1')
        self.assertEqual(Story.objects.get(pk=2).headline, 'Changed 2')

    def _post_admin_action(self, action):
        change_dict = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MAX_NUM_FORMS': '',
            'action': 'set_status_to_%s' % action,
            'select_across': '0',
            '_selected_action': '1',
            'index': '0',
            'form-0-id': '1',
            'form-1-id': '2',
            'form-0-status': '3',
            'form-0-headline': 'Changed 1',
            'form-0-subhead': '',
            'form-0-kicker': '',
            'form-0-status': '3',
            'form-0-teaser': '',
            'form-1-status': '3',
            'form-1-headline': 'Changed 2',
            'form-1-subhead' : '',
            'form-1-kicker': '',
            'form-1-status': '3',
            'form-1-teaser': '',
        }
        return self.client.post('/admin/stories/story/', change_dict)

    def test_admin_actions(self):
        self.assertTrue(self.client.login(username='admin', password='pass'))

        post = self._post_admin_action('DRAFT')
        self.assertRedirects(post, '/admin/stories/story/')
        self.assertEquals(Story.objects.get(pk=1).status, 1)
        post = self._post_admin_action('READY FOR EDITING')
        self.assertRedirects(post, '/admin/stories/story/')
        self.assertEquals(Story.objects.get(pk=1).status, 2)
        post = self._post_admin_action('READY TO PUBLISH')
        self.assertRedirects(post, '/admin/stories/story/')
        self.assertEquals(Story.objects.get(pk=1).status, 3)
        post = self._post_admin_action('PUBLISHED')
        self.assertRedirects(post, '/admin/stories/story/')
        self.assertEquals(Story.objects.get(pk=1).status, 4)
        post = self._post_admin_action('REJECTED')
        self.assertRedirects(post, '/admin/stories/story/')
        self.assertEquals(Story.objects.get(pk=1).status, 5)
        post = self._post_admin_action('UN-PUBLISHED')
        self.assertRedirects(post, '/admin/stories/story/')
        self.assertEquals(Story.objects.get(pk=1).status, 6)


class AuthorTests(BaseTests):
    fixtures = ['auth.json', 'profile.json', 'basicauthor.json', 'stories.json']
    def test_field_type(self):
        from simpleapp.models import BasicAuthor
        field, a, b, c = Story._meta.get_field_by_name('authors')
        self.assertEqual(field.rel.to, BasicAuthor)

    def test_field_meta(self):
        """This test is here to test getting some meta values that
        is used on the initial south migration"""
        field, a, b, c = Story._meta.get_field_by_name('authors')
        self.assertEqual(field.m2m_reverse_name(), 'basicauthor_id')
        self.assertEqual(field.m2m_reverse_field_name(), 'basicauthor')

    def test_field_query(self):
        self.assertEqual(self.story1.authors.all().count(), 2)
        self.assertEqual(self.story2.authors.all().count(), 2)

        users = User.objects.filter(pk__in=[2,4])
        for author in self.story1.authors.all():
            self.assertIn(author.user, users)

        users = User.objects.filter(pk__in=[3, 5])
        for author in self.story2.authors.all():
            self.assertIn(author.user, users)


class RelationTests(BaseTests):
    fixtures = ['auth.json', 'profile.json', 'videos.json',
                'photos.json', 'stories.json']

    def setUp(self):
        super(RelationTests, self).setUp()
        from simpleapp.models import BasicPhoto, BasicVideo
        self.photo1 = BasicPhoto.objects.get(pk=1)
        self.photo1 = BasicPhoto.objects.get(pk=2)
        self.video1 = BasicVideo.objects.get(pk=1)
        self.video2 = BasicVideo.objects.get(pk=2)

        self.photo_ctype = ContentType.objects.get_for_model(BasicPhoto)
        self.video_ctype = ContentType.objects.get_for_model(BasicVideo)

    def _create_rels(self):
        from stories.relations.models import StoryRelation
        rel1 = StoryRelation.objects.create(
            story=self.story1,
            content_type=self.photo_ctype, object_id=1)

        rel2 = StoryRelation.objects.create(
            story=self.story2,
            content_type=self.video_ctype, object_id=1,
            relation_type="Regular")

        rel3 = StoryRelation.objects.create(
            story=self.story2,
            content_type=self.video_ctype, object_id=2,
            relation_type="Regular")

        return rel1, rel2, rel3

    def test_has_relation_attrs(self):
        self.assertTrue(hasattr(self.story1, 'get_related_content_type'))
        self.assertTrue(hasattr(self.story1, 'get_relation_type'))

    def test_related_methods(self):
        from stories.relations.models import StoryRelation
        rel1, rel2, rel3 = self._create_rels()

        items = self.story1.get_related_content_type('basic photo')
        manager_items = StoryRelation.objects.get_content_type('basic photo')
        self.assertEqual(list(items), [rel1])
        self.assertEqual(list(manager_items), [rel1])

        items = self.story2.get_relation_type("Regular")
        manager_items = StoryRelation.objects.get_relation_type('Regular')
        self.assertEqual(list(items), [rel2, rel3])
        self.assertEqual(list(manager_items), [rel2, rel3])

    def test_change_form(self):
        from stories.relations.models import StoryRelation

        rel1, rel2, rel3 = self._create_rels()

        self.assertTrue(self.client.login(username='admin', password='pass'))
        self.assertEqual(
            self.client.get('/admin/stories/story/1/').status_code, 200)

        change_dict = {
            'headline': 'Changed',
            'slug': 'changed',
            'body': "<p>This is the body</p>",
            'status': '1',
            'origin': '0',
            'comment_status': '0',
            'site': '1',
            'publish_date': '2012-03-14',
            'publish_time': '00:00:00',

            # The required story relation form data
            'storyrelation_set-TOTAL_FORMS': '4',
            'storyrelation_set-INITIAL_FORMS': '1',
            'storyrelation_set-MAX_NUM_FORMS': '',

            'storyrelation_set-0-id': rel1.pk,
            'storyrelation_set-0-story': rel1.story.pk,
            'storyrelation_set-0-content_type': rel1.content_type.pk,
            'storyrelation_set-0-object_id': rel1.object_id,
            'storyrelation_set-0-relation_type': 'Changed',
        }

        cf_post = self.client.post('/admin/stories/story/1/', change_dict)
        self.assertRedirects(cf_post, '/admin/stories/story/')
        self.assertEqual(Story.objects.get(pk=1).headline, 'Changed')

        self.assertEqual(StoryRelation.objects.get(pk=1).relation_type, 'Changed')

    def test_tt_get_related_content(self):
        self._create_rels()
        tmpl = '{% load story_relation_tags %}'\
               '{% get_related_content story as story_rels %}'\
               '{% for rel in story_rels %}'\
                   '{{ rel.content_object.pk }},'\
               '{% endfor %}'

        ctx = {'story': self.story2}
        self.assertEqual(render(tmpl, ctx), '1,2,')

    def test_tt_get_related_content_type(self):
        self._create_rels()
        tmpl = '{% load story_relation_tags %}'\
               '{% get_related_content_type story "basic photo" as photos %}'\
               '{% for photo in photos %}'\
                   '{{ photo.pk }},'\
               '{% endfor %}'

        ctx = {'story': self.story1}
        self.assertEqual(render(tmpl, ctx), '1,')

    def test_tt_get_relation_type(self):
        self._create_rels()
        tmpl = '{% load story_relation_tags %}'\
               '{% get_relation_type story Regular as reg_items %}'\
               '{% for item in reg_items %}'\
                   '{{ item.pk }},'\
               '{% endfor %}'

        ctx = {'story': self.story2}
        self.assertEqual(render(tmpl, ctx), '2,3,')


class PrintTests(BaseTests):
    def test_has_fields(self):
        self.assertTrue(hasattr(self.story1, 'print_pub_date'))
        self.assertTrue(hasattr(self.story1, 'print_section'))
        self.assertTrue(hasattr(self.story1, 'print_page'))

    def test_saving(self):
        date = datetime.datetime.now()
        self.story1.print_pub_date = date
        self.story1.print_section = 'feature'
        self.story1.print_page = '1a'
        self.story1.save()

        self.assertEqual(self.story1.print_pub_date, date)
        self.assertEqual(self.story1.print_section, 'feature')
        self.assertEqual(self.story1.print_page, '1a')


class CategoryTests(BaseTests):
    fixtures = ['auth.json', 'profile.json',
                'categories.json', 'stories_with_cats.json']

    def setUp(self):
        super(CategoryTests, self).setUp()
        from categories.models import Category

        self.cat1 = Category.objects.get(pk=1)
        self.cat2 = Category.objects.get(pk=2)
        self.cat3 = Category.objects.get(pk=3)

    def test_has_fields(self):
        from categories.fields import CategoryM2MField, CategoryFKField

        self.assertTrue(hasattr(self.story1, 'primary_category'))
        self.assertTrue(hasattr(self.story1, 'categories'))

        self.assertEqual(
            Story._meta.get_field('primary_category').__class__,
            CategoryFKField)

        self.assertEqual(
            Story._meta.get_field('categories').__class__,
            CategoryM2MField)

    def test_field_data(self):
        self.assertEqual(self.story1.primary_category, self.cat1)

        s1_cat_ids = [c.pk for c in self.story1.categories.all()]
        s2_cat_ids = [c.pk for c in self.story2.categories.all()]

        self.assertTrue(self.cat2.pk in s1_cat_ids)
        self.assertTrue(self.cat3.pk in s1_cat_ids)

        self.assertTrue(self.cat2.pk in s2_cat_ids)
        self.assertFalse(self.cat3.pk in s2_cat_ids)


class WidgetTests(BaseTests):
    def test_load_widget(self):
        from example.simpleapp.widgets import CustomTextarea

        self.assertEqual(load_widget(settings.WIDGET), CustomTextarea)
        self.assertRaises(ImproperlyConfigured, load_widget, path='bad.module')
