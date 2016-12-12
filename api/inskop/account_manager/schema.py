from django.contrib.auth.models import User
from graphene import AbstractType, Mutation, Int, String, Field, Boolean, Node, ID
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_relay import from_global_id

from ..account_manager.functions import user_star_counter
from ..account_manager.models import Auth0User, AuthorizationLevel
from ..code_manager.models import Code
from ..scene_manager.models import Scene, Analysis


class Auth0UserNode(DjangoObjectType):
    class Meta:
        model = Auth0User
        filter_fields = ['auth0_id']
        interfaces = (Node,)

    scene_stars = Int()
    code_stars = Int()
    analysis_stars = Int()
    is_current_user = Boolean()

    def resolve_scene_stars(self, args, context, info):
        return user_star_counter(self, Scene)

    def resolve_code_stars(self, args, context, info):
        return user_star_counter(self, Code)

    def resolve_analysis_stars(self, args, context, info):
        return user_star_counter(self, Analysis)

    def resolve_is_current_user(self, args, context, info):
        try:
            current_user = Auth0User.objects.get(user=context.user)
            is_current_user = current_user == self
        except:
            is_current_user = False
        return is_current_user

class AuthorizationLevelNode(DjangoObjectType):
    class Meta:
        model = AuthorizationLevel
        interfaces = (Node,)


class Query(AbstractType):
    all_auth0users = DjangoFilterConnectionField(Auth0UserNode)
    auth0user_by_slug = Field(Auth0UserNode, slug=String(required=True))

    def resolve_auth0user_by_slug(self, args, context, info):
        slug = args.get('slug')
        try:
            auth0User = Auth0User.objects.get(slug=slug)
        except:
            auth0User = None
        return auth0User


class AddAuth0User(Mutation):
    # Required args from mutation query
    class Input:
        name = String(required=True)
        email = String(required=True)
        picture = String(required=True)
        auth0Id = String(required=True)

    # Payload to return after mutation
    auth0_user = Field(Auth0UserNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        # Get data from mutation query
        name = args.get('name')
        email = args.get('email')
        picture = args.get('picture')
        auth0Id = args.get('auth0Id')
        try:
            auth0User = Auth0User.objects.get(auth0_id=auth0Id)
            auth0User.name = name
            auth0User.email = email
            auth0User.picture = picture
            auth0User.save()
        except:
            user = User.objects.create_user(username=name)
            auth0User = Auth0UserNode._meta.model(auth0_id=auth0Id, name=name, email=email, picture=picture, user=user)
            auth0User.save()

        return AddAuth0User(auth0_user=auth0User, ok=bool(auth0User.id))


class ChangeAuth0User(Mutation):
    # Required args from mutation query
    class Input:
        user_id = ID(required=True)
        bio = String(required=False)

    # Payload to return after mutation
    auth0_user = Field(Auth0UserNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        # Get data from mutation query
        user_pk = from_global_id(args.get('user_id'))[1]
        auth0User = Auth0User.objects.get(pk=user_pk)
        bio = args.get('bio')
        if context.user == auth0User.user:
            auth0User.bio = bio
            auth0User.save()

        return ChangeAuth0User(auth0_user=auth0User, ok=bool(auth0User.id))


class Mutation(AbstractType):
    add_auth0User = AddAuth0User.Field()
    change_auth0User = ChangeAuth0User.Field()
