import os
import tempfile
from shutil import copyfile

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from inskop.account_manager.models import Auth0User
from inskop.code_manager.models import Process, Code, CodeCategory
from inskop.scene_manager.models import Scene, FavoriteScene, Camera, Video, TagTarget, TagCategory, Tag


class SceneTestCase(TestCase):
    fixtures = ['account_data_test', 'code_data_test', 'scene_data_test']
    
    def setUp(self):
        settings.MEDIA_ROOT = tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
        vid_src = 'media/testfiles/vid.mp4'
        vid_dst1 = os.path.join(settings.MEDIA_ROOT, 'scenes/michel_scene/cam1/orig.mp4')
        video1 = Video.objects.get(pk=1)
        video1.file = vid_dst1
        video1.save()
        os.makedirs(os.path.dirname(vid_dst1), exist_ok=True)
        copyfile(vid_src, vid_dst1)
        vid_dst2 = os.path.join(settings.MEDIA_ROOT, 'scenes/monique_scene/cam1/orig.mp4')
        video2 = Video.objects.get(pk=2)
        video2.file = vid_dst2
        video2.save()
        os.makedirs(os.path.dirname(vid_dst2), exist_ok=True)
        copyfile(vid_src, vid_dst2)
        # User 1 creates process and scene


    def test_scene_has_name(self):
        """Scene has a name"""
        scene1 = Scene.objects.get(name='michel_scene')
        self.assertEqual(scene1.__str__(), 'michel_scene')

    def test_scene_has_frame_count(self):
        """Scene has a frame_count property"""
        scene1 = Scene.objects.get(name='michel_scene')
        self.assertEqual(scene1.frame_count, 284)

    def test_scene_has_fps(self):
        """Scene has a fps property"""
        scene1 = Scene.objects.get(name='michel_scene')
        self.assertEqual(scene1.fps, 29)

    def test_scene_has_duration(self):
        """Scene has a duration property"""
        scene1 = Scene.objects.get(name='michel_scene')
        self.assertEqual(scene1.duration, 9.793103448275861)

    def test_scene_has_favorite_count(self):
        """Scene has a favorite_count property"""
        scene1 = Scene.objects.get(name='michel_scene')
        self.assertEqual(scene1.favorite_count, 1)
        scene2 = Scene.objects.get(name='monique_scene')
        self.assertEqual(scene2.favorite_count, 0)

    def test_scene_has_is_user_favorite(self):
        """Scene has a is_user_favorite method"""
        scene1 = Scene.objects.get(name='michel_scene')
        auth0user1 = Auth0User.objects.get(auth0_id='michel_auth0id')
        auth0user2 = Auth0User.objects.get(auth0_id='monique_auth0id')
        self.assertTrue(not scene1.is_user_favorite(user=auth0user1))
        self.assertTrue(scene1.is_user_favorite(user=auth0user2))


class TagTestCase(TestCase):
    fixtures = ['account_data_test', 'code_data_test', 'scene_data_test']

    def test_tag_target_has_name(self):
        """TagTarget has a name"""
        tag_target = TagTarget.objects.get(name='selection')
        self.assertEqual(tag_target.__str__(), 'selection')

    def test_tag_category_has_name(self):
        """TagCategory has a name"""
        tag_category = TagCategory.objects.get(name='main')
        self.assertEqual(tag_category.__str__(), 'main')

    def test_tag_has_name(self):
        """Tag has a name"""
        tag = Tag.objects.get(name='bird')
        self.assertEqual(tag.__str__(), 'bird')
