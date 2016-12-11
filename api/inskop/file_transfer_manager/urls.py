from django.conf.urls import url

from ..file_transfer_manager import views

urlpatterns = [
    url(r'upload/scenes/(?P<filename>[^/]+)$', views.FileUploadView.as_view(), name='upload_view'),
    url(r'download/windows', views.windows_view, name='download_view')
]
