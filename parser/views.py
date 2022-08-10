from rest_framework import viewsets, pagination

from parser.models import LinkedinUsers
from parser.serializers import CheckMyUserSerializers


class PageNumberSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    ordering = 'created_at'


class CheckMyUserView(viewsets.ModelViewSet):
    queryset = LinkedinUsers.objects.all()
    serializer_class = CheckMyUserSerializers
    pagination_class = PageNumberSetPagination
