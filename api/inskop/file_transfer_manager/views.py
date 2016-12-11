import os

from django.conf import settings
from rest_framework import response
from rest_framework import views, parsers
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_csv.renderers import CSVRenderer

from ..account_manager.models import Auth0User
from ..scene_manager.models import Window, Scene


# Switch to rest-pandas

class WindowRenderer(CSVRenderer):
    header = ['selection', 't', 'x', 'y']


@api_view(['GET'])
@renderer_classes((WindowRenderer,))
def windows_view(request):
    windows = Window.objects.all()
    content = [{'selection': window.selection.name,
                't': window.t,
                'x': window.x,
                'y': window.y}
               for window in windows]
    return response.Response(content)


class FileUploadView(views.APIView):
    parser_classes = (parsers.FileUploadParser,)

    def put(self, request, filename):
        file = request.data['file']
        scene_name = filename
        handle_uploaded_file(file, scene_name)
        return response.Response(status=204)


def handle_uploaded_file(file, scene_name):
    if file.size > 20000000:
        return
    new_scene = Scene.objects.create(name=scene_name, owner=Auth0User.objects.get(name='temp_user'), active=False)
    dir_name = settings.MEDIA_ROOT + '/scenes/' + new_scene.slug + '/cam1'
    file_name = 'orig.mp4'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    file_path = os.path.join(dir_name, file_name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    new_scene.delete()
