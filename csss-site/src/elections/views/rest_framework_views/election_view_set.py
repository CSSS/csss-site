from rest_framework import serializers, viewsets
from rest_framework.response import Response

from about.models import Term
from csss.views.rest_framework_views.pagination import StandardResultsSetPagination
from elections.models import Election


class ElectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Election
        fields = '__all__'


class ElectionViewSet(viewsets.ModelViewSet):
    serializer_class = ElectionSerializer
    queryset = Election.objects.all().order_by('-date')
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        return Response("not yet implemented")

    def update(self, request, *args, **kwargs):
        return Response("not yet implemented")
