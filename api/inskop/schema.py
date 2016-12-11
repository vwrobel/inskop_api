import graphene
from graphene_django.debug import DjangoDebug
import inskop.account_manager.schema
import inskop.code_manager.schema
import inskop.other_manager.schema
import inskop.scene_manager.schema


class Query(inskop.scene_manager.schema.Query,
            inskop.code_manager.schema.Query,
            inskop.account_manager.schema.Query,
            inskop.other_manager.schema.Query,
            graphene.ObjectType
            ):
    debug = graphene.Field(DjangoDebug, name='__debug')


class Mutation(inskop.scene_manager.schema.Mutation,
               inskop.code_manager.schema.Mutation,
               inskop.account_manager.schema.Mutation,
               graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')


schema = graphene.Schema(query=Query, mutation=Mutation)
