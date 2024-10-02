from django.utils.safestring import mark_safe

from base.admin import BaseAdmin, my_admin_site
from rental.models import *


class RoomAdmin(BaseAdmin):
	list_display = ["name", "number_of_bed", "type", "room_for"]
	list_filter = ["number_of_bed", "type", "room_for"]
	search_fields = ["name"]
	readonly_fields = ["room_image"]

	def room_image(self, instance):
		if instance:
			return mark_safe(f"<img width='512' src='{instance.image.url}' />")


class PostAdmin(BaseAdmin):
	list_display = ["id", "name"]
	search_fields = ["name"]
	readonly_fields = ["post_image"]

	def post_image(self, instance):
		if instance:
			return mark_safe(f"<img width='512' src='{instance.image.url}' />")


class BedAdmin(BaseAdmin):
	list_display = ["name", "price", "status"]
	list_filter = ["room__number_of_bed", "room__type", "room__room_for"]
	search_fields = ["room__name"]
	readonly_fields = ["bed_image"]

	def bed_image(self, instance):
		if instance:
			return mark_safe(f"<img width='512' src='{instance.image.url}' />")


class RentalContactAdmin(BaseAdmin):
	list_display = ["rental_number", "time_rental", "status"]
	list_filter = ["status"]
	search_fields = ["rental_number", "time_rental", "status"]


class BillRentalAdmin(BaseAdmin):
	list_display = ["bill_number", "total", "status"]
	list_filter = ["status"]
	search_fields = ["bill_number", "total", "status"]


class ViolateNoticeAdmin(BaseAdmin):
	list_display = ["id", "violate_number"]
	search_fields = ["violate_number"]


class ElectricityAndWaterBillsAdmin(BaseAdmin):
	list_display = ["total_cubic_meters_water", "total_electricity", "total_amount", "status"]
	list_filter = ["total_cubic_meters_water", "total_electricity", "total_amount", "status"]


my_admin_site.register(Room, RoomAdmin)
my_admin_site.register(Post, PostAdmin)
my_admin_site.register(Bed, BedAdmin)
my_admin_site.register(RentalContact, RentalContactAdmin)
my_admin_site.register(BillRentalContact, BillRentalAdmin)
my_admin_site.register(ViolateNotice, ViolateNoticeAdmin)
my_admin_site.register(ElectricityAndWaterBills, ElectricityAndWaterBillsAdmin)
