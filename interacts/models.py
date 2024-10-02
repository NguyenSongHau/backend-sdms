from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from base.models import BaseModel


class Interaction(BaseModel):
	class Meta:
		abstract = True

	user = models.ForeignKey(to="users.User", null=False, blank=False, on_delete=models.CASCADE, related_name="%(class)ss")
	post = models.ForeignKey(to="rental.Post", null=False, blank=False, on_delete=models.CASCADE, related_name="%(class)ss")


class Comment(Interaction):
	content = CKEditor5Field("Text", config_name="extends")


class Like(Interaction):
	class Meta:
		unique_together = ("user", "post")
