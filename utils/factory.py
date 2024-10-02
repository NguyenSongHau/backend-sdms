from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rental.models import RentalContact
from utils import validations


def set_role_for_account(user, account):
	role = validations.check_user_instance(user)[1]

	if not role:
		raise ValidationError({"detail": "Người dùng không hợp lệ"})

	account.role = role
	account.save()

	return user, account


def update_status(rental_contact, new_status, message):
	if rental_contact.status != RentalContact.Status.PROCESSING:
		return Response(data={"message": "Hồ sơ đã được xử lý."}, status=status.HTTP_400_BAD_REQUEST)

	rental_contact.status = new_status
	rental_contact.save()

	return Response(data={"message": message}, status=status.HTTP_200_OK)


def to_float(value):
	try:
		return float(value)
	except (ValueError, TypeError):
		raise ValidationError(f"Vui lòng nhập đúng định dạng.")


def get_all_subclasses(cls):
	all_subclasses = []

	for subclass in cls.__subclasses__():
		if not subclass._meta.abstract:
			all_subclasses.append(subclass)
		all_subclasses.extend(get_all_subclasses(subclass))

	return all_subclasses
