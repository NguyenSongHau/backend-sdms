from rest_framework import permissions

from users.models import User


class OwnerComment(permissions.IsAuthenticated):
	def has_object_permission(self, request, view, comment):
		return super().has_permission(request, view) and request.user == comment.user


class IsA(permissions.IsAuthenticated):
	role = None

	def has_permission(self, request, view):
		return super().has_permission(request, view) and request.user.role == self.role


class IsAdmin(IsA):
	role = User.Role.ADMINISTRATOR.value


class IsManager(IsA):
	role = User.Role.MANAGER


class IsSpecialist(IsA):
	role = User.Role.SPECIALIST


class IsStudent(IsA):
	role = User.Role.STUDENT
