from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseModel


class User(AbstractUser, BaseModel):
	class Role(models.TextChoices):
		ADMINISTRATOR = "AD", _("Administrator")
		SPECIALIST = "SPC", _("Chuyên viên cộng tác sinh viên")
		MANAGER = "MAG", _("Quản lý")
		STUDENT = "STU", _("Sinh viên")

	class Gender(models.TextChoices):
		MALE = "M", _("Nam")
		FEMALE = "F", _("Nữ")
		UNKNOWN = "U", _("Khác")

	email = models.EmailField(null=False, blank	=False, unique=True, db_index=True)
	avatar = CloudinaryField("images", null=True, blank=True)
	full_name = models.CharField(max_length=255, null=False, blank=False)
	dob = models.DateField(null=False, blank=False)
	gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.UNKNOWN)
	address = models.CharField(max_length=255, null=False, blank=False)
	phone = models.CharField(max_length=15, null=False, blank=False)
	identification = models.CharField(max_length=12, null=False, blank=False, unique=True, db_index=True)
	role = models.CharField(max_length=10, null=False, blank=False, choices=Role.choices, default=Role.STUDENT)

	username = None
	first_name = None
	last_name = None

	from users.managers import UserManager
	objects = UserManager()

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = []

	def __str__(self):
		return f"{self.full_name} - {self.email}"

	@property
	def original_role(self):
		return self.Role.labels[self.Role.values.index(self.role)]

	@property
	def original_gender(self):
		return self.Gender.labels[self.Role.values.index(self.gender)]

	@staticmethod
	def get_role_from_string(role_str):
		role_str_lower = role_str.lower()
		try:
			index = User.Role.labels.index(role_str_lower)
			return User.Role.values[index]
		except ValueError:
			return None


class Administrator(BaseModel):
	user = models.OneToOneField(to=User, null=False, blank=False, on_delete=models.CASCADE, related_name="%(class)s")

	def __str__(self):
		return self.user.email


class Manager(BaseModel):
	certificate = models.CharField(max_length=255, null=False, blank=False)

	user = models.OneToOneField(to=User, null=False, blank=False, on_delete=models.CASCADE, related_name="%(class)s")

	def __str__(self):
		return self.user.email


class Specialist(BaseModel):
	degree = models.CharField(max_length=255, null=False, blank=False)

	user = models.OneToOneField(to=User, null=False, blank=False, on_delete=models.CASCADE, related_name="%(class)s")

	def __str__(self):
		return self.user.email


class Student(BaseModel):
	student_id = models.CharField(max_length=10, null=False, blank=False, db_index=True)
	university = models.CharField(max_length=255, null=False, blank=False)
	faculty = models.CharField(max_length=255, null=False, blank=False)
	major = models.CharField(max_length=255, null=False, blank=False)
	academic_year = models.IntegerField(null=False, blank=False)

	user = models.OneToOneField(to=User, null=False, blank=False, on_delete=models.CASCADE, related_name="%(class)s")

	def __str__(self):
		return self.user.email
