from django.contrib import admin

from ..scene_manager.models import Video, Scene, Window, Camera, Tag, TagCategory, TagTarget, \
    Selection, FavoriteScene, WindowType, SearchZone, SearchZoneType, Analysis, FavoriteAnalysis, SceneStatus

# Register your models here.
model_list = [Scene, Camera, Window, Tag, TagCategory, TagTarget, FavoriteScene,
              WindowType, SearchZone, SearchZoneType, Analysis, FavoriteAnalysis, SceneStatus]  # iterable list
admin.site.register(model_list)


class VideoAdmin(admin.ModelAdmin):
    list_display = ('get_scene', 'analysis', 'name')

    def get_scene(self, obj):
        return obj.camera.scene.name

    get_scene.short_description = 'Scene'
    get_scene.admin_order_field = 'video__camera__scene__name'


admin.site.register(Video, VideoAdmin)


class SelectionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'analysis')


admin.site.register(Selection, SelectionAdmin)
