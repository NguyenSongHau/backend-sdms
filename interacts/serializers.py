from rest_framework import serializers

from base.serializers import BaseSerializer
from interacts.models import Comment
from users import serializers as users_serializer


class CommentSerializer(BaseSerializer):
	user = serializers.SerializerMethodField()

	class Meta:
		model = Comment
		fields = ["id", "content", "created_date", "updated_date", "user"]

	def get_user(self, comment):
		serializer = users_serializer.UserSerializer(comment.user)

		return serializer.data
