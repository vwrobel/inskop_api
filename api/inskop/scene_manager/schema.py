import os

from django.db.models import Q
from graphene import Mutation, AbstractType, Node, Int, String, Field, Boolean, Float, ID
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_relay.node.node import from_global_id

from ..account_manager.models import Auth0User
from ..code_manager.models import Process, Code
from ..scene_manager.models import Scene, SceneStatus, Camera, Video, Window, Tag, TagCategory, \
    TagTarget, Selection, FavoriteScene, WindowType, Analysis, SelectionType, FavoriteAnalysis
from ..scene_manager.services import process_vid

class SceneNode(DjangoObjectType):
    class Meta:
        model = Scene
        interfaces = (Node,)
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'slug': ['exact', 'icontains', 'istartswith'],
            'description': ['icontains'],
            'owner': ['exact'],
            'owner__name': ['exact'],
            'owner__auth0_id': ['exact'],
            'created_at': ['exact'],
            'locked': ['exact']
        }
        filter_order_by = ['name', 'owner', 'owner__auth0_id', 'created_at', 'description']

    favorite_count = Int()
    is_user_favorite = Boolean()
    is_user_owner = Boolean()
    frame_count = Int()
    duration = Float()
    fps = Float()
    thumbnail = String()

    def resolve_is_user_favorite(self, args, context, info):
        try:
            user = Auth0User.objects.get(user=context.user)
            is_user_favorite = self.is_user_favorite(user)
        except:
            is_user_favorite = False
        return is_user_favorite

    def resolve_is_user_owner(self, args, context, info):
        try:
            user = Auth0User.objects.get(user=context.user)
            is_user_owner = self.is_user_owner(user)
        except:
            is_user_owner = False
        return is_user_owner

    def resolve_fps(self, args, context, info):
        return self.fps

    def resolve_favorite_count(self, args, context, info):
        return self.favorite_count

    def resolve_frame_count(self, args, context, info):
        return self.frame_count

    def resolve_thumbnail(self, args, context, info):
        return self.thumbnail

    def resolve_duration(self, args, context, info):
        return self.duration

    @classmethod
    def get_node(cls, id, context, info):
        try:
            scene = cls._meta.model.objects.get(id=id)
        except cls._meta.model.DoesNotExist:
            return None

        if not scene.locked or context.user == scene.owner:
            return scene
        return None


class FavoriteSceneNode(DjangoObjectType):
    class Meta:
        model = FavoriteScene


class SceneStatusNode(DjangoObjectType):
    class Meta:
        model = SceneStatus


class CameraNode(DjangoObjectType):
    class Meta:
        model = Camera
        # Allow for some more advanced filtering here
        filter_fields = {
            'scene': ['exact'],
            'number': ['exact']
        }
        filter_order_by = ['number']
        interfaces = (Node,)

    name = String()

    def resolve_name(self, args, context, info):
        return self.__str__()


class VideoNode(DjangoObjectType):
    class Meta:
        model = Video
        # Allow for some more advanced filtering here
        filter_fields = {
            'analysis__id': ['exact'],
            'camera__scene__slug': ['exact'],
            'camera': ['exact'],
            'process': ['exact']
        }
        filter_order_by = ['camera__scene__name']
        interfaces = (Node,)


class AnalysisNode(DjangoObjectType):
    class Meta:
        model = Analysis
        # Allow for some more advanced filtering here
        filter_fields = {
            'scene__name': ['exact'],
            'scene__slug': ['exact'],
            'owner__name': ['exact']
        }
        filter_order_by = ['scene']
        interfaces = (Node,)

    favorite_count = Int()
    is_user_favorite = Boolean()
    is_user_owner = Boolean()

    def resolve_is_user_favorite(self, args, context, info):
        try:
            user = Auth0User.objects.get(user=context.user)
            is_user_favorite = self.is_user_favorite(user)
        except:
            is_user_favorite = False
        return is_user_favorite

    def resolve_is_user_owner(self, args, context, info):
        try:
            user = Auth0User.objects.get(user=context.user)
            is_user_owner = self.is_user_owner(user)
        except:
            is_user_owner = False
        return is_user_owner

    def resolve_favorite_count(self, args, context, info):
        return self.favorite_count


class FavoriteAnalysisNode(DjangoObjectType):
    class Meta:
        model = FavoriteAnalysis


class SelectionNode(DjangoObjectType):
    class Meta:
        model = Selection
        # Allow for some more advanced filtering here
        filter_fields = {
            'analysis': ['exact'],
            'analysis__name': ['exact'],
            'analysis__scene__name': ['exact']
        }
        filter_order_by = ['analysis']
        interfaces = (Node,)

    pk = Int()

    def resolve_pk(self, args, context, info):
        return self.pk


class SelectionTypeNode(DjangoObjectType):
    class Meta:
        model = SelectionType
        interfaces = (Node,)


class WindowTypeNode(DjangoObjectType):
    class Meta:
        model = WindowType
        interfaces = (Node,)


class WindowNode(DjangoObjectType):
    class Meta:
        model = Window
        # Allow for some more advanced filtering here
        filter_fields = {
            'camera__scene__name': ['exact'],
            'camera': ['exact'],
            't': ['exact'],
            'selection': ['exact'],
            'selection__analysis': ['exact'],
            'type__name': ['exact']
        }
        filter_order_by = ['camera__scene__name']
        interfaces = (Node,)


class TagNode(DjangoObjectType):
    class Meta:
        model = Tag
        # Allow for some more advanced filtering here
        filter_fields = {
            'name': ['exact']
        }
        filter_order_by = ['name']
        interfaces = (Node,)


class TagCategoryNode(DjangoObjectType):
    class Meta:
        model = TagCategory
        # Allow for some more advanced filtering here
        filter_fields = {
            'name': ['exact']
        }
        filter_order_by = ['name']
        interfaces = (Node,)


class Query(AbstractType):
    scene = Node.Field(SceneNode)
    scene_by_slug = Field(SceneNode, slug=String())
    all_scenes = DjangoFilterConnectionField(SceneNode)
    selected_scenes = DjangoFilterConnectionField(SceneNode, excludeOwner=Boolean(), excludeFavorite=Boolean())

    def resolve_scene_by_slug(self, args, context, info):
        slug = args.get('slug')
        try:
            scene = Scene.objects.get(slug=slug)
        except:
            scene = None
        return scene

    def resolve_selected_scenes(self, args, context, info):
        user = Auth0User.objects.get(user=context.user)
        exclude_owner = args.get('excludeOwner')
        exclude_favorite = args.get('excludeFavorite')
        selected_scenes = Scene.manager.select_scenes(user, exclude_owner, exclude_favorite)
        return selected_scenes

    camera = Node.Field(CameraNode)
    all_cameras = DjangoFilterConnectionField(CameraNode)

    video = Node.Field(VideoNode)
    orig_video = DjangoFilterConnectionField(VideoNode)

    def resolve_orig_video(self, args, context, info):
        scene_slug = args.get('camera__scene__slug')
        orig_video = Video.objects.get(camera__scene__slug=scene_slug, process__slug='orig')
        return [orig_video]

    all_videos = DjangoFilterConnectionField(VideoNode)
    all_videos_of_analysis = DjangoFilterConnectionField(VideoNode)

    def resolve_all_videos_of_analysis(self, args, context, info):
        analysis_pk = from_global_id(args.get('analysis__id'))[1]
        videos_of_analysis = Video.objects.filter(analysis__pk=analysis_pk, active=True)
        return videos_of_analysis

    analysis = Node.Field(AnalysisNode)
    all_analyses = DjangoFilterConnectionField(AnalysisNode)

    def resolve_all_analyses(self, args, context, info):
        slug = args.get('scene__slug')
        scene = Scene.objects.get(slug=slug)
        user = Auth0User.objects.get(user=context.user)
        visible_analyses = Analysis.objects.filter((Q(owner=user) | Q(locked=False)) & Q(active=True) & Q(scene=scene))
        return visible_analyses

    window = Node.Field(WindowNode)
    all_windows = DjangoFilterConnectionField(WindowNode)

    selection = Node.Field(SelectionNode)
    all_selections = DjangoFilterConnectionField(SelectionNode)

    tag = Node.Field(TagNode)
    all_tags = DjangoFilterConnectionField(TagNode, tag_target=String(), tag_category=String())

    def resolve_all_tags(self, args, context, info):
        tag_target = TagTarget.objects.get(name=args.get('tag_target'))
        tag_category = TagCategory.objects.get(name=args.get('tag_category'), target=tag_target)
        visible_tags = Tag.objects.filter(category=tag_category)
        return visible_tags

    tagCategory = Node.Field(TagCategoryNode)
    all_tagCategories = DjangoFilterConnectionField(TagCategoryNode)


class AddVideo(Mutation):
    class Input:
        analysis_id = ID(required=True)
        camera_number = Int(required=True)
        process_name = String(required=True)
        process_yaml = String(required=True)

    video = Field(VideoNode)
    ok = Boolean()
    status_url = String()

    def mutate(self, args, context, info):
        analysis = Analysis.objects.get(pk=from_global_id(args.get('analysis_id'))[1])
        camera = Camera.objects.get(number=args.get('camera_number'), scene=analysis.scene)
        process_name = args.get('process_name')
        process_yaml = args.get('process_yaml')
        owner = Auth0User.objects.get(user=context.user)
        try:
            process = Process.objects.get(name=process_name, owner=owner)
            process.process = process_yaml
            process.save()
            try:
                video = Video.object.get(camera=camera, process=process, analysis=analysis)
                video.delete()
            except:
                pass
        except:
            process = Process.objects.create(name=process_name, process=process_yaml, owner=owner)
        video = Video.objects.create(
            camera=camera,
            process=process,
            analysis=analysis,
            name=process_name
        )
        video.file.name = video.get_path()
        video.save()
        try:
            os.remove(video.get_path(with_mediaroot=True))
        except OSError:
            pass
        status_url = process_vid(video)
        return AddVideo(video=video, status_url=status_url, ok=bool(video.id))


class ChangeVideo(Mutation):
    class Input:
        video_id = ID(required=True)
        process_yaml = String(required=True)

    video = Field(VideoNode)
    status_url = String()
    ok = Boolean()

    def mutate(self, args, context, info):
        video = Video.objects.get(pk=from_global_id(args.get('video_id'))[1])
        process_yaml = args.get('process_yaml')
        user = Auth0User.objects.get(user=context.user)
        status_url = ''
        if video.analysis.owner == user:
            process = video.process;
            process.process = process_yaml
            process.save()
            status_url = process_vid(video)
        return ChangeVideo(video=video, status_url=status_url, ok=bool(video.id))


class DeleteVideo(Mutation):
    class Input:
        video_id = ID(required=True)

    video = Field(VideoNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        video = Video.objects.get(pk=from_global_id(args.get('video_id'))[1])
        user = Auth0User.objects.get(user=context.user)
        if video.analysis.owner == user and video.slug is not 'orig':
            video.active = False
            video.save()
        return DeleteVideo(video=video, ok=bool(video.id))


class AddScene(Mutation):
    class Input:
        name = String(required=True)
        description = String(required=True)
        status = String(required=True)

    scene = Field(SceneNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        name = args.get('name')
        description = args.get('description')
        status = SceneStatus.objects.get(name=args.get('status'))
        user = Auth0User.objects.get(user=context.user)
        scene = SceneNode._meta.model(
            name=name,
            description=description,
            owner=user,
            status=status
        )
        scene.save()
        scene.create_camera()
        scene.create_orig_vid()
        scene.create_thumbnail()
        return AddScene(scene=scene, ok=bool(scene.id))


class DeleteScene(Mutation):
    class Input:
        scene_id = String(required=True)

    scene = Field(SceneNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        user = Auth0User.objects.get(user=context.user)
        pk = from_global_id(args.get('scene_id'))[1]
        scene = Scene.objects.get(pk=pk)
        if user == scene.owner:
            scene.active = False
            scene.save()
            return DeleteScene(scene=scene, ok=True)


class ChangeScene(Mutation):
    class Input:
        scene_id = String(required=True)
        name = String(required=False)
        description = String(required=False)
        status = String(required=False)

    scene = Field(SceneNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        pk = from_global_id(args.get('scene_id'))[1]
        name = args.get('name')
        description = args.get('description')
        status = SceneStatus.objects.get(name=args.get('status'))
        scene = Scene.objects.get(pk=pk)
        if description != 'undefined' and description != '':
            scene.description = description
        if status:
            scene.status = status
        scene.save()
        return ChangeScene(scene=scene, ok=bool(scene.id))


class AddSelection(Mutation):
    class Input:
        analysis_id = ID(required=True)
        name = String(required=True)
        main_tag = String(required=True)

    selection = Field(SelectionNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        analysis = Analysis.objects.get(pk=from_global_id(args.get('analysis_id'))[1])
        user = Auth0User.objects.get(user=context.user)
        if user != analysis.owner:
            return
        try:
            selection = Selection.objects.get(analysis=analysis, name=args.get('name'))
        except:
            selection = SelectionNode._meta.model(analysis=analysis, name=args.get('name'))
            selection.save()
            tag_target = TagTarget.objects.get(name='selection')
            tag_category = TagCategory.objects.get(name='main', target=tag_target)
            main_tag = Tag.objects.get(category=tag_category, name=args.get('main_tag'))
            selection.tags.add(main_tag)
            selection.save()
        return AddSelection(selection=selection, ok=bool(selection.id))


class AddTag(Mutation):
    class Input:
        tag_name = String(required=True)
        tag_category = String(required=True)
        tag_target = String(required=True)

    tag = Field(TagNode)
    ok = Boolean()
    exists = Boolean()

    def mutate(self, args, context, info):
        user = Auth0User.objects.get(user=context.user)
        tag_target = TagTarget.objects.get(name=args.get('tag_target'))
        tag_category = TagCategory.objects.get(name=args.get('tag_category'), target=tag_target)
        try:
            tag = Tag.objects.get(name=args.get('tag_name'), category=tag_category)
            exists = True
        except:
            tag = TagNode._meta.model(name=args.get('tag_name'), owner=user, category=tag_category)
            tag.save()
            exists = False
        return AddTag(tag=tag, ok=bool(tag.id), exists=exists)


class AddWindow(Mutation):
    class Input:
        selection_id = ID(required=True)
        camera_number = Int(required=True)
        t = Float(required=True)
        json_item = String(required=True)

    window = Field(WindowNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        t = args.get('t')
        user = Auth0User.objects.get(user=context.user)
        selection = Selection.objects.get(pk=from_global_id(args.get('selection_id'))[1])
        if user != selection.analysis.owner:
            return
        camera = Camera.objects.get(number=args.get('camera_number'), scene=selection.analysis.scene)
        type = WindowType.objects.get(name='manual')
        json_item = args.get('json_item')
        window = WindowNode._meta.model(selection=selection, camera=camera, t=t, type=type, json_item=json_item)
        window.save()
        return AddWindow(window=window, ok=bool(window.id))


class AddAnalysis(Mutation):
    class Input:
        scene_id = ID(required=True)
        name = String(required=True)
        description = String(required=True)

    analysis = Field(AnalysisNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        scene = Scene.objects.get(pk=from_global_id(args.get('scene_id'))[1])
        user = Auth0User.objects.get(user=context.user)
        analysis = AnalysisNode._meta.model(
            scene=scene,
            owner=user,
            name=args.get('name'),
            description=args.get('description')
        )
        analysis.save()
        return AddAnalysis(analysis=analysis, ok=bool(analysis.id))


class DeleteAnalysis(Mutation):
    class Input:
        analysisId = String(required=True)

    analysis = Field(AnalysisNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        user = Auth0User.objects.get(user=context.user)
        pk = from_global_id(args.get('analysisId'))[1]
        analysis = Analysis.objects.get(pk=pk)
        if user == analysis.owner:
            analysis.active = False
            analysis.save()
            return DeleteAnalysis(analysis=analysis, ok=True)


class ChangeAnalysis(Mutation):
    class Input:
        analysis_id = String(required=True)
        name = String(required=False)
        description = String(required=False)

    analysis = Field(AnalysisNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        pk = from_global_id(args.get('analysis_id'))[1]
        name = args.get('name')
        description = args.get('description')
        analysis = Analysis.objects.get(pk=pk)
        if description != 'undefined' and description != '':
            analysis.description = description
        analysis.save()
        return ChangeAnalysis(analysis=analysis, ok=bool(analysis.id))


class UnlockAnalysis(Mutation):
    class Input:
        analysisId = String(required=True)

    analysis = Field(AnalysisNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        pk = from_global_id(args.get('analysisId'))[1]
        analysis = Analysis.objects.get(pk=pk)
        analysis.locked = not analysis.locked
        analysis.save()
        return UnlockAnalysis(analysis=analysis, ok=bool(analysis.id))


class StarAnalysis(Mutation):
    class Input:
        analysisId = String(required=True)

    analysis = Field(AnalysisNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        pk = from_global_id(args.get('analysisId'))[1]
        analysis = Analysis.objects.get(pk=pk)
        user = Auth0User.objects.get(user=context.user)
        favoriteAnalysis = FavoriteAnalysis.objects.filter(analysis=analysis, user=user)
        if favoriteAnalysis:
            favoriteAnalysis.delete()
        else:
            favoriteAnalysis = FavoriteAnalysisNode._meta.model(analysis=analysis, user=user)
            favoriteAnalysis.save()
        return StarAnalysis(analysis=analysis, ok=bool(analysis.id))


class ClearAnalysis(Mutation):
    class Input:
        analysis_id = ID(required=True)

    analysis = Field(AnalysisNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        analysis = Analysis.objects.get(pk=from_global_id(args.get('analysis_id'))[1])
        user = Auth0User.objects.get(user=context.user)
        if user == analysis.owner:
            Selection.objects.filter(analysis=analysis).delete()
            return ClearAnalysis(analysis=analysis, ok=bool(analysis.id))


class UnlockScene(Mutation):
    class Input:
        sceneId = String(required=True)

    scene = Field(SceneNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        pk = from_global_id(args.get('sceneId'))[1]
        scene = Scene.objects.get(pk=pk)
        scene.locked = not scene.locked
        scene.save()
        return UnlockScene(scene=scene, ok=bool(scene.id))


class StarScene(Mutation):
    class Input:
        sceneId = String(required=True)

    scene = Field(SceneNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        pk = from_global_id(args.get('sceneId'))[1]
        scene = Scene.objects.get(pk=pk)
        user = Auth0User.objects.get(user=context.user)
        favoriteScene = FavoriteScene.objects.filter(scene=scene, user=user)
        if favoriteScene:
            favoriteScene.delete()
        else:
            favoriteScene = FavoriteSceneNode._meta.model(scene=scene, user=user)
            favoriteScene.save()
        return StarScene(scene=scene, ok=bool(scene.id))


class Mutation(AbstractType):
    add_scene = AddScene.Field()
    change_scene = ChangeScene.Field()
    delete_scene = DeleteScene.Field()
    star_scene = StarScene.Field()
    unlock_scene = UnlockScene.Field()
    add_selection = AddSelection.Field()
    add_window = AddWindow.Field()
    add_analysis = AddAnalysis.Field()
    change_analysis = ChangeAnalysis.Field()
    delete_analysis = DeleteAnalysis.Field()
    star_analysis = StarAnalysis.Field()
    unlock_analysis = UnlockAnalysis.Field()
    clear_analysis = ClearAnalysis.Field()
    add_tag = AddTag.Field()
    add_video = AddVideo.Field()
    delete_video = DeleteVideo.Field()
    change_video = ChangeVideo.Field()
