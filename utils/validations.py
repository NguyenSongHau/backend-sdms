from datetime import datetime

from rest_framework.exceptions import ValidationError

from users.models import User, Administrator, Manager, Specialist, Student


def check_user_instance(user):
	if not isinstance(user, (Administrator, Specialist, Manager, Student)):
		raise ValidationError({"message": "Người dùng không hợp lệ"})

	from users import serializers
	instance_mapping = {
		Administrator: (serializers.AdministratorSerializer, User.Role.ADMINISTRATOR),
		Specialist: (serializers.SpecialistSerializer, User.Role.SPECIALIST),
		Manager: (serializers.ManagerSerializer, User.Role.MANAGER),
		Student: (serializers.StudentSerializer, User.Role.STUDENT),
	}

	return instance_mapping.get(type(user))


def check_user_role(user):
	if not isinstance(user, User):
		raise ValidationError({"message": "Tài khoản không hợp lệ"})

	from users import serializers
	role_mapping = {
		User.Role.ADMINISTRATOR: (serializers.AdministratorSerializer, "administrator"),
		User.Role.SPECIALIST: (serializers.SpecialistSerializer, "specialist"),
		User.Role.MANAGER: (serializers.ManagerSerializer, "manager"),
		User.Role.STUDENT: (serializers.StudentSerializer, "student"),
	}

	return role_mapping.get(user.role)


def validate_date(date):
	try:
		datetime.strptime(date, "%Y-%m-%d")
	except ValueError:
		return False

	return date
