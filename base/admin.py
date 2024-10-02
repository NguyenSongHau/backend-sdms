from django.contrib import admin


# from django.contrib.auth.models import Group, Permission


class MyAdminSite(admin.AdminSite):
	site_header = "SDMS Administator"
	site_title = "SDMS site admin"
	index_title = "Quản lý ký túc xá sinh viên"


class BaseAdmin(admin.ModelAdmin):
	list_per_page = 20
	list_max_show_all = 100


my_admin_site = MyAdminSite(name="Student Dormitory Management System")

# my_admin_site.register(Group)
# my_admin_site.register(Permission)
