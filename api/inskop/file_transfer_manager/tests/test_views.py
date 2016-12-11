import os
import tempfile

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from inskop.account_manager.models import Auth0User


class UploadVideoTestCase(APITestCase):
    def setUp(self):
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        User.objects.create_user('michel')
        temp_user = User.objects.create_user('temp_user')
        Auth0User.objects.create(user=temp_user, name='temp_user', auth0_id='temp_user')

    def test_video_uploaded(self):
        """Video uploaded"""
        scene_name = 'myscene'
        file = File(open('media/testfiles/vid.mp4', 'rb'))
        uploaded_file = SimpleUploadedFile(scene_name, file.read(), content_type='multipart/form-data')
        client = APIClient()
        user = User.objects.get(username='michel')
        client.force_authenticate(user=user)
        url = reverse('file_upload:upload_view', kwargs={'filename': scene_name})
        client.put(url, {'file': uploaded_file}, format='multipart')
        dir_name = settings.MEDIA_ROOT + '/scenes/' + scene_name + '/cam1'
        file_name = 'orig.mp4'
        file_path = os.path.join(dir_name, file_name)
        self.assertTrue(os.path.exists(file_path))
