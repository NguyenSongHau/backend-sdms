from rest_framework import generics, viewsets, status
from rest_framework.response import Response

from base import perms, paginators
from interacts import serializers as interacts_serializers
from interacts.models import Comment


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView):
	queryset = Comment.objects.select_related("user", "post").filter(is_active=True)
	serializer_class = interacts_serializers.CommentSerializer
	pagination_class = paginators.CommentPaginators
	permission_classes = [perms.OwnerComment]

	def update(self, request, pk=None):
		serializer = self.serializer_class(instance=self.get_object(), data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data=serializer.data, status=status.HTTP_200_OK)
