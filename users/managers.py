from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
	def create_user(self, email=None, password=None, **extra_fields):
		if not email:
			raise ValueError(_("Email must be set"))

		if not password:
			raise ValueError(_("Password must be set"))

		user = self.create(email=self.normalize_email(email.strip()), password=make_password(password), **extra_fields)

		return user

	def create_superuser(self, email=None, password=None, **extra_fields):
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("full_name", "ADMINISTRATOR")
		extra_fields.setdefault("dob", timezone.now())
		extra_fields.setdefault("role", self.model.Role.ADMINISTRATOR)

		from users.models import Administrator
		user = self.create_user(email=email, password=password, **extra_fields)
		Administrator.objects.create(user=user)

		return user
