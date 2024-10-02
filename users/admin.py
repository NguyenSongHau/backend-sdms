from django.utils.safestring import mark_safe

from base.admin import BaseAdmin, my_admin_site
from users.models import User, Administrator, Manager, Specialist, Student


class UserAdmin(BaseAdmin):
	list_display = ["email", "role", "is_staff", "is_superuser", "is_active", "last_login", "date_joined"]
	list_filter = ["role", "is_staff", "is_superuser", "is_active", "last_login", "date_joined"]
	search_fields = ["email"]
	readonly_fields = ["user_avatar"]

	def user_avatar(self, instance):
		if instance:
			return mark_safe(f"<img width='512' src='{instance.image.url}' />")

	def save_model(self, request, obj, form, change):
		if not obj.pk or 'password' in form.changed_data:
			obj.set_password(obj.password)
		super().save_model(request, obj, form, change)


class AdministratorAdmin(BaseAdmin):
	pass


class ManagerAdmin(BaseAdmin):
	list_display = ["id", "certificate"]
	list_filter = ["user__role", "user__is_staff", "user__is_superuser", "user__is_active", "user__last_login", "user__date_joined"]
	search_fields = ["user__email", "certificate"]


class SpecialistAdmin(BaseAdmin):
	list_display = ["id", "degree"]
	list_filter = ["user__role", "user__is_staff", "user__is_superuser", "user__is_active", "user__last_login", "user__date_joined"]
	search_fields = ["user__email", "degree"]


class StudentAdmin(BaseAdmin):
	list_display = ["id", "student_id", "university", "faculty", "major", "academic_year"]
	list_filter = ["user__role", "user__is_staff", "user__is_superuser", "user__is_active", "user__last_login", "user__date_joined"]
	search_fields = ["user__email", "student_id", "university", "faculty", "major", "academic_year"]


my_admin_site.register(User, UserAdmin)
my_admin_site.register(Administrator, AdministratorAdmin)
my_admin_site.register(Manager, ManagerAdmin)
my_admin_site.register(Specialist, SpecialistAdmin)
my_admin_site.register(Student, StudentAdmin)
