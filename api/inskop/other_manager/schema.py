from graphene import AbstractType, Field, Node
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from ..other_manager.models import Doc


class DocNode(DjangoObjectType):
    class Meta:
        model = Doc
        filter_fields = ['title']
        filter_order_by = ['title']
        interfaces = (Node,)


class Query(AbstractType):
    doc = Field(DocNode)
    all_docs = DjangoFilterConnectionField(DocNode)
