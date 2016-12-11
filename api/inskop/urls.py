from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from graphene_django.views import GraphQLView
from jwt_auth.mixins import JSONWebTokenAuthMixin
from jwt_auth.utils import get_authorization_header


class OptionalJWTMixin(JSONWebTokenAuthMixin):
    def dispatch(self, request, *args, **kwargs):
        auth = get_authorization_header(request)
        if auth:
            return super(OptionalJWTMixin, self).dispatch(request, *args, **kwargs)
        else:
            return super(JSONWebTokenAuthMixin, self).dispatch(request, *args, **kwargs)


class AuthGraphQLView(OptionalJWTMixin, GraphQLView):
    pass


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graphql', csrf_exempt(AuthGraphQLView.as_view(graphiql=True))),
    url(r'^rest/v1/file_transfer/', include('inskop.file_transfer_manager.urls', namespace='file_upload'))
]

if settings.DEBUG:
    urlpatterns.append(
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
    )
