import uuid

from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from base.models import BaseModel
from utils.constants import NUMBER_OF_BED_NORMAL_ROOM, NUMBER_OF_BED_SERVICE_ROOM, PRICE_OF_BED_NORMAL_ROOM, PRICE_OF_BED_SERVICE_ROOM


class Room(BaseModel):
	class Type(models.TextChoices):
		NORMAL = "NORMAL", "Phòng thường"
		SERVICE = "SERVICE", "Phòng dịch vụ"

	class RoomFor(models.TextChoices):
		MALE = "M", "Nam"
		FEMALE = "F", "Nữ"

	name = models.CharField(max_length=255, null=False, blank=False)
	image = models.ImageField(upload_to='', null=True, blank=True)
	number_of_bed = models.IntegerField(null=True, blank=True)
	type = models.CharField(max_length=255, null=False, blank=False, choices=Type.choices, default=Type.NORMAL)
	room_for = models.CharField(max_length=255, null=False, blank=False, choices=RoomFor.choices, default=RoomFor.MALE)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if self.number_of_bed is None:
			self.number_of_bed = NUMBER_OF_BED_NORMAL_ROOM if self.type == self.Type.NORMAL else NUMBER_OF_BED_SERVICE_ROOM
		super().save(*args, **kwargs)


class Post(BaseModel):
	name = models.CharField(max_length=255, null=False, blank=False)
	image = models.ImageField(upload_to='', null=True, blank=True)
	description = CKEditor5Field("Text", config_name="extends")

	room = models.OneToOneField(to=Room, null=False, blank=False, on_delete=models.CASCADE, related_name="post")

	def __str__(self):
		return self.name


class Bed(BaseModel):
	class Status(models.TextChoices):
		VACUITY = "VACUITY", "Trống"
		NONVACUITY = "NONVACUITY", "Đã thuê"

	name = models.CharField(max_length=255, null=False, blank=False)
	price = models.FloatField(null=True, blank=True)
	image = models.ImageField(upload_to='', null=True, blank=True)
	description = CKEditor5Field("Text", config_name="extends")
	status = models.CharField(max_length=255, null=False, blank=False, choices=Status.choices, default=Status.VACUITY)

	room = models.ForeignKey(to=Room, null=False, blank=False, on_delete=models.CASCADE, related_name="beds")

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if self.price is None:
			self.price = PRICE_OF_BED_NORMAL_ROOM if self.room.type == Room.Type.NORMAL else PRICE_OF_BED_SERVICE_ROOM
		super().save(*args, **kwargs)


class RentalContact(BaseModel):
	objects = None

	class Status(models.TextChoices):
		CANCEL = "CANCEL", "Đã Hủy"
		PROCESSING = "PROCESSING", "Đang xử lý"
		SUCCESS = "SUCCESS", "Thành công"
		FAIL = "FAIL", "Từ chối"

	rental_number = models.UUIDField(null=False, blank=False, unique=True, db_index=True, editable=False, default=uuid.uuid4)
	time_rental = models.CharField(max_length=255, null=False, blank=False)
	status = models.CharField(max_length=255, null=False, blank=False, choices=Status.choices, default=Status.PROCESSING)

	bed = models.OneToOneField(to=Bed, null=True, blank=True, on_delete=models.SET_NULL, related_name="rental_contact")
	student = models.ForeignKey(to="users.Student", null=False, blank=False, on_delete=models.CASCADE, related_name="rental_contacts")
	room = models.ForeignKey(to=Room, null=True, blank=True, on_delete=models.SET_NULL, related_name="rental_contact")

class BillRentalContact(BaseModel):
	class Status(models.TextChoices):
		PAID = "PAID", "Đã thanh toán"
		UNPAID = "UNPAID", "Chưa thanh toán"

	bill_number = models.UUIDField(null=False, blank=False, unique=True, db_index=True, editable=False, default=uuid.uuid4)
	total = models.FloatField(null=False, blank=False)
	status = models.CharField(max_length=255, null=False, blank=False, choices=Status.choices, default=Status.UNPAID)

	student = models.ForeignKey(to="users.Student", null=False, blank=False, on_delete=models.CASCADE, related_name="bill_rental_contact")
	specialist = models.ForeignKey(to="users.Specialist", null=False, blank=False, on_delete=models.CASCADE, related_name="bill_rental_contact")
	rental_contact = models.OneToOneField(to=RentalContact, null=False, blank=False, on_delete=models.CASCADE, related_name="bill_rental_contact")


class ViolateNotice(BaseModel):
	violate_number = models.UUIDField(null=False, blank=False, unique=True, db_index=True, editable=False, default=uuid.uuid4)
	description = CKEditor5Field("Text", config_name="extends")

	room = models.ForeignKey(to=Room, null=False, blank=False, on_delete=models.CASCADE, related_name="violate_notices")
	manager = models.ForeignKey(to="users.Manager", null=True, blank=True, on_delete=models.SET_NULL, related_name="violate_notices")


class ElectricityAndWaterBills(BaseModel):
	class Status(models.TextChoices):
		PAID = "PAID", "Đã thanh toán"
		UNPAID = "UNPAID", "Chưa thanh toán"

	total_cubic_meters_water = models.FloatField(null=False, blank=False)
	total_electricity = models.FloatField(null=False, blank=False)
	total_amount = models.FloatField(null=False, blank=False)
	status = models.CharField(max_length=255, null=False, blank=False, choices=Status.choices, default=Status.UNPAID)

	room = models.ForeignKey(to=Room, null=False, blank=False, on_delete=models.CASCADE, related_name="electricity_and_water_bills")
	manager = models.ForeignKey(to="users.Manager", null=True, blank=True, on_delete=models.SET_NULL, related_name="electricity_and_water_bills")
