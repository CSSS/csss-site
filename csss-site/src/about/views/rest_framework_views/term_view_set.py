from rest_framework import serializers, viewsets
from rest_framework.response import Response

from about.models import Term
from csss.views.rest_framework_views.pagination import StandardResultsSetPagination


class TermSerializer(serializers.ModelSerializer):

    class Meta:
        model = Term
        fields = '__all__'


class TermViewSet(viewsets.ModelViewSet):
    serializer_class = TermSerializer
    queryset = Term.objects.all().order_by('-term_number')
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        return Response("not yet implemented")

    def update(self, request, *args, **kwargs):
        return Response("not yet implemented")