from __future__ import unicode_literals

import base64
import json
import os.path

import cv2
from PIL import Image
from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.db.models import Q
from webcolors import hex_to_rgb
from ..account_manager.models import Auth0User
from ..code_manager.models import Process
from ..storage import OverwriteStorage


class TagTarget(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TagCategory(models.Model):
    name = models.CharField(max_length=50)
    target = models.ForeignKey(TagTarget, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(TagCategory, on_delete=models.CASCADE)
    owner = models.ForeignKey(Auth0User)

    def __str__(self):
        return self.name


class SceneManager(models.Manager):
    def select_scenes(self, user, exclude_owner, exclude_favorite):
        selected_scenes = self.model.objects.filter(Q(active=True) & (Q(owner=user) | Q(locked=False)))
        if exclude_owner:
            selected_scenes = selected_scenes.exclude(owner=user)
        else:
            selected_scenes = selected_scenes.filter(owner=user)
        if exclude_favorite is not None:
            if exclude_favorite:
                selected_scenes = [scene for scene in selected_scenes if not scene.is_user_favorite(user)]
            else:
                selected_scenes = [scene for scene in selected_scenes if scene.is_user_favorite(user)]
        return selected_scenes


class SceneStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Scene(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(Auth0User)
    slug = AutoSlugField(populate_from='name', always_update=True, unique=True)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=400, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=400, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    locked = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    valid = models.BooleanField(default=True)
    status = models.ForeignKey(SceneStatus, blank=True, null=True)
    objects = models.Manager()
    manager = SceneManager()

    def __str__(self):
        return self.name

    @property
    def orig_vid(self):
        camera = Camera.objects.get(scene=self, number=1)
        orig_vid = Video.objects.get(camera=camera, process__slug='orig')
        return orig_vid

    @property
    def orig_cap(self):
        orig_vid = self.orig_vid
        orig_cap = cv2.VideoCapture(orig_vid.get_path(with_mediaroot=True))
        return orig_cap

    @property
    def frame_count(self):
        cap = self.orig_cap
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return frame_count

    @property
    def fps(self):
        cap = self.orig_cap
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        return fps

    @property
    def duration(self):
        frame_count = self.frame_count
        fps = self.fps
        duration = frame_count / fps
        return duration

    @property
    def favorite_count(self):
        favorite_scene = FavoriteScene.objects.filter(scene=self).exclude(user=self.owner)
        favorite_count = len(favorite_scene)
        return favorite_count

    @property
    def thumbnail(self):
        orig_vid = self.orig_vid
        thumbnail_path = orig_vid.get_thumbnail_path(with_mediaroot=False)
        return thumbnail_path

    def is_user_favorite(self, user):
        user_favorite = FavoriteScene.objects.filter(user=user, scene=self)
        return len(user_favorite) > 0

    def is_user_owner(self, user):
        return self.owner == user

    def create_camera(self):
        try:
            Camera.objects.get(scene=self, number=1)
        except:
            Camera.objects.create(scene=self, number=1)

    def create_orig_vid(self):
        camera = Camera.objects.get(scene=self, number=1)
        orig_process = Process.objects.get(slug='orig')
        try:
            video = Video.objects.get(camera=camera, process=orig_process, name='orig')
        except:
            video = Video.objects.create(camera=camera, process=orig_process, name='orig')
        video.file.name = video.get_path()
        video.save()

    def create_thumbnail(self):
        size = 280, 158
        orig_vid = self.orig_vid
        thumbnail_file_jpg = orig_vid.get_thumbnail_path(with_mediaroot=True)
        thumbnail_exists = os.path.isfile(thumbnail_file_jpg)
        if not thumbnail_exists:
            thumbnail_file_png = thumbnail_file_jpg.replace('jpg', 'png')
            thumbnail_img = orig_vid.get_img_b64(0)
            thumbnail_img = base64.decodebytes(bytes(thumbnail_img, 'utf-8'))
            with open(thumbnail_file_png, "wb") as fh:
                fh.write(thumbnail_img)
            im = Image.open(thumbnail_file_png)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(thumbnail_file_jpg, "JPEG")


class FavoriteScene(models.Model):
    scene = models.ForeignKey(Scene)
    user = models.ForeignKey(Auth0User)

    def __str__(self):
        return self.user.name + '_' + self.scene.name


class Camera(models.Model):
    number = models.IntegerField()
    description = models.CharField(max_length=400, null=True, blank=True)
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)

    def __str__(self):
        return self.scene.name + '_' + self.name

    @property
    def name(self):
        return 'cam' + str(self.number)


class Analysis(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    owner = models.ForeignKey(Auth0User, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, blank=True, null=True)
    slug = AutoSlugField(populate_from='name', always_update=True, unique_with=('scene'))
    description = models.CharField(max_length=400, blank=True, null=True)
    locked = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.scene.name + '_' + self.owner.name + '_' + self.name

    @property
    def favorite_count(self):
        favorite_analysis = FavoriteAnalysis.objects.filter(analysis=self).exclude(user=self.owner)
        favorite_count = len(favorite_analysis)
        return favorite_count

    def is_user_favorite(self, user):
        user_favorite = FavoriteAnalysis.objects.filter(user=user, analysis=self)
        return len(user_favorite) > 0

    def is_user_owner(self, user):
        return self.owner == user


class FavoriteAnalysis(models.Model):
    analysis = models.ForeignKey(Analysis)
    user = models.ForeignKey(Auth0User)

    def __str__(self):
        return self.user.name + '_' + self.analysis.name


def video_path(instance, filename=''):
    # file will be uploaded to MEDIA_ROOT/...
    if instance.process.slug == 'orig':
        return 'scenes/{0}/{1}/orig.mp4'.format(instance.camera.scene.slug, instance.camera.name)
    else:
        return 'scenes/{0}/{1}/analyses/{2}/{3}/{4}.mp4'.format(
            instance.camera.scene.slug,
            instance.camera.name,
            instance.analysis.owner.slug,
            instance.analysis.slug,
            instance.slug)


class Video(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=40, null=True, blank=True)
    slug = AutoSlugField(populate_from='name', always_update=True, unique_with=('camera'))
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    file = models.FileField(upload_to=video_path, storage=OverwriteStorage(), null=True)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.slug

    def get_img(self, t):
        cap = self.get_cap()
        cap.set(cv2.CAP_PROP_POS_FRAMES, t)
        ret, img = cap.read()
        cap.release()
        return img

    def get_img_b64(self, t):
        img = self.get_img(t)
        img_str = cv2.imencode('.jpg', img)[1].tostring()
        img_b64 = base64.b64encode(img_str).decode()
        return img_b64

    def get_path(self, with_mediaroot=False):
        if with_mediaroot:
            if not settings.MEDIA_URL:
                path = os.path.join(settings.MEDIA_ROOT, video_path(self))
            else:
                path = os.path.join(settings.MEDIA_URL, video_path(self))
        else:
            path = video_path(self)
        return path

    def get_dirname(self, with_mediaroot=False):
        return os.path.dirname(self.get_path(with_mediaroot))

    def get_filename(self, with_mediaroot=False):
        return os.path.basename(self.get_path(with_mediaroot))

    def get_thumbnail_path(self, with_mediaroot=False):
        return os.path.join(self.get_dirname(with_mediaroot), 'thumbnail.jpg')

    def get_cap(self, with_details=False):
        vid_path = self.get_path(with_mediaroot=True)
        cap = cv2.VideoCapture(vid_path)
        ret = cap
        if with_details:
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            details = [frame_count, fps, frame_width, frame_height]
            ret = [cap] + details
        return ret


class SelectionType(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Selection(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    tags = models.ManyToManyField(Tag, blank=True)
    type = models.ForeignKey(SelectionType, blank=True, null=True)

    def __str__(self):
        return str(self.analysis) + '_' + self.name


class SearchZoneType(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class SearchZone(models.Model):
    camera = models.ForeignKey(Camera)
    type = models.ForeignKey(SearchZoneType)
    json_item = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        return self.camera.__str__()


class WindowType(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Window(models.Model):
    selection = models.ForeignKey(Selection, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    t = models.IntegerField()
    type = models.ForeignKey(WindowType, blank=True, null=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, null=True)
    json_item = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        return self.selection.analysis.__str__() + '_t_' + str(self.t)

    @property
    def item(self):
        return json.loads(self.json_item)

    @property
    def x(self):
        return self.item['x']

    @property
    def y(self):
        return self.item['y']

    @property
    def w(self):
        return self.item['width']

    @property
    def h(self):
        return self.item['height']

    @property
    def color(self):
        r, g, b = hex_to_rgb(self.item['stroke'])
        return b, g, r

    @property
    def bounds(self):
        return [self.x, self.y, self.w, self.h]

    @property
    def selection_dict(self):
        selection_dict = {
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h,
            't': self.t,
            'color': self.color,
            'name': self.selection.name,
            'type': self.type.name
        }
        return selection_dict
