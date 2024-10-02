from base.admin import BaseAdmin, my_admin_site
from interacts.models import Comment, Like


class CommentAdmin(BaseAdmin):
	list_display = ["user", "post", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("content", "user__email", "post__name",)


class LikeAdmin(BaseAdmin):
	list_display = ["user", "post", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("user__email", "post__name",)


my_admin_site.register(Comment, CommentAdmin)
my_admin_site.register(Like, LikeAdmin)
