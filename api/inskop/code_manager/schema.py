from django.db.models import Q
from graphene import Mutation, AbstractType, Int, String, Field, Boolean, Node
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_relay.node.node import from_global_id

from ..account_manager.models import Auth0User
from ..code_manager.models import Process, Code, CodeCategory, FavoriteCode


class ProcessNode(DjangoObjectType):
    class Meta:
        model = Process
        filter_fields = ['name']
        filter_order_by = ['name']
        interfaces = (Node,)


class FavoriteCodeNode(DjangoObjectType):
    class Meta:
        model = FavoriteCode
        interfaces = (Node,)


class CodeNode(DjangoObjectType):
    class Meta:
        model = Code
        filter_fields = ['category__name', 'name']
        filter_order_by = ['name']
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


class CodeCategoryNode(DjangoObjectType):
    class Meta:
        model = CodeCategory
        filter_fields = ['name']
        filter_order_by = ['category__name']
        interfaces = (Node,)


class Query(AbstractType):
    process = Field(ProcessNode)
    all_processes = DjangoFilterConnectionField(ProcessNode)

    code = Field(CodeNode)
    all_codes = DjangoFilterConnectionField(CodeNode)

    def resolve_all_codes(self, args, context, info):
        codes = Code.objects.exclude(category__name='orig')
        codes = codes.filter(Q(active=True) & (Q(owner__user=context.user) | Q(valid=True)))
        return codes

    code_by_slug = Field(CodeNode, slug=String())

    def resolve_code_by_slug(self, args, context, info):
        slug = args.get('slug')
        try:
            code = Code.objects.get(slug=slug)
        except:
            code = None
        return code

    all_filters = DjangoFilterConnectionField(CodeNode)

    def resolve_all_filters(self, args, context, info):
        filters = Code.objects.filter(category__name='video filter')
        return filters

    all_trackers = DjangoFilterConnectionField(CodeNode)

    def resolve_all_trackers(self, args, context, info):
        filters = Code.objects.filter(category__name='tracker')
        return filters

    category = Field(CodeCategoryNode)
    all_code_categories = DjangoFilterConnectionField(CodeCategoryNode)


class AddCode(Mutation):
    class Input:
        name = String(required=True)
        description = String(required=True)
        category = String(required=True)

    code = Field(CodeNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        name = args.get('name')
        description = args.get('description')
        category = CodeCategory.objects.get(name=args.get('category'))
        user = Auth0User.objects.get(user=context.user)
        code = CodeNode._meta.model(name=name, description=description, owner=user, category=category)
        code.save()
        return AddCode(code=code, ok=bool(code.id))


class DeleteCode(Mutation):
    class Input:
        codeId = String(required=True)

    code = Field(CodeNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        user = Auth0User.objects.get(user=context.user)
        pk = from_global_id(args.get('codeId'))[1]
        code = Code.objects.get(pk=pk)
        if user == code.owner:
            code.active = False
            code.save()
            return DeleteCode(code=code, ok=True)


class ChangeCode(Mutation):
    class Input:
        code_id = String(required=True)
        name = String(required=False)
        description = String(required=False)
        category = String(required=False)

    code = Field(CodeNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        pk = from_global_id(args.get('code_id'))[1]
        name = args.get('name')
        description = args.get('description')
        category = args.get('category')
        code = Code.objects.get(pk=pk)
        if description != 'undefined' and description != '':
            code.description = description
        if category != 'undefined' and category != '':
            code.category = CodeCategory.objects.get(name=category)
        code.save()
        return ChangeCode(code=code, ok=bool(code.id))


class EditCode(Mutation):
    class Input:
        code_id = String(required=True)
        code_chunk = String(required=False)
        read_me = String(required=False)

    code = Field(CodeNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        pk = from_global_id(args.get('code_id'))[1]
        code_chunk = args.get('code_chunk')
        read_me = args.get('read_me')
        code = Code.objects.get(pk=pk)
        if code_chunk != 'undefined' and code_chunk != '':
            code.code = code_chunk
        if read_me != 'undefined' and read_me != '':
            code.read_me = read_me
        code.save()
        return EditCode(code=code, ok=bool(code.id))


class UnlockCode(Mutation):
    class Input:
        codeId = String(required=True)

    code = Field(CodeNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        pk = from_global_id(args.get('codeId'))[1]
        code = Code.objects.get(pk=pk)
        code.locked = not code.locked
        code.save()
        return UnlockCode(code=code, ok=bool(code.id))


class StarCode(Mutation):
    class Input:
        codeId = String(required=True)

    code = Field(CodeNode)
    ok = Boolean()

    def mutate(self, args, context, info):
        pk = from_global_id(args.get('codeId'))[1]
        code = Code.objects.get(pk=pk)
        user = Auth0User.objects.get(user=context.user)
        favoriteCode = FavoriteCode.objects.filter(code=code, user=user)
        if favoriteCode:
            favoriteCode.delete()
        else:
            favoriteCode = FavoriteCodeNode._meta.model(code=code, user=user)
            favoriteCode.save()
        return StarCode(code=code, ok=bool(code.id))


class Mutation(AbstractType):
    add_code = AddCode.Field()
    change_code = ChangeCode.Field()
    edit_code = EditCode.Field()
    delete_code = DeleteCode.Field()
    star_code = StarCode.Field()
    unlock_code = UnlockCode.Field()
