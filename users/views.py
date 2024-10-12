from django.contrib.auth.hashers import check_password
from rest_framework import parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from base import perms, paginators
from base.paginators import UserPagination
from rental import serializers as rental_serializers
from users import serializers as users_serializers
from users.models import User, Specialist, Manager
from users.serializers import SpecialistSerializer, ManagerSerializer, UserSerializer


class UserViewSet(viewsets.ViewSet):
	queryset = User.objects.filter(is_active=True)
	serializer_class = users_serializers.UserSerializer
	parser_classes = [parsers.MultiPartParser, ]

	def get_queryset(self):
		queryset = self.queryset

		queryset = queryset.prefetch_related("rental_contacts") if self.action.__eq__("get_all_rental_contacts") else queryset

		return queryset

	def get_permissions(self):
		if self.action in ["current_user", "update_current_user"]:
			return [permissions.IsAuthenticated()]

		if self.action in ["get_all_rental_contacts"]:
			return [perms.IsStudent()]

		return [permissions.AllowAny()]

	@action(methods=["post"], detail=False, url_path="register")
	def register(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data={"message": "Đăng ký tài khoản thành công."}, status=status.HTTP_201_CREATED)

	@action(methods=["get"], detail=False, url_path="current-user")
	def current_user(self, request):
		serializer = self.serializer_class(request.user)

		return Response(data=serializer.data, status=status.HTTP_200_OK)

	@action(methods=["patch"], detail=False, url_path="current-user/update")
	def update_current_user(self, request):
		old_password = request.data.get("old_password", None)
		new_password = request.data.get("new_password", None)

		if old_password and new_password and not check_password(old_password, request.user.password):
			return Response(data={"detail": "Mật khẩu cũ không chính xác"}, status=status.HTTP_400_BAD_REQUEST)

		serializer = users_serializers.UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data=serializer.data, status=status.HTTP_200_OK)

	@action(methods=["get"], detail=False, url_path="students/rental-contacts")
	def get_all_rental_contacts(self, request):
		student = request.user.student
		rental_status = request.query_params.get("status")
		rental_contacts = student.rental_contacts.filter(status=rental_status.upper()) if rental_status else student.rental_contacts.all()

		paginator = paginators.RentalContactPaginators()
		page = paginator.paginate_queryset(queryset=rental_contacts, request=request)
		if page is not None:
			serializer = rental_serializers.RentalContactSerializer(page, many=True)
			return paginator.get_paginated_response(serializer.data)

		serializer = rental_serializers.RentalContactSerializer(rental_contacts, many=True)
		return Response(data=serializer.data, status=status.HTTP_200_OK)

	from users.serializers import UserSerializer

	@action(detail=False, methods=["get"], url_path="specialists-managers")
	def get_all_specialists_and_managers(self, request):
		# Lấy tất cả chuyên viên và quản lý đang active
		specialists = Specialist.objects.filter(user__is_active=True)
		managers = Manager.objects.filter(user__is_active=True)

		# Lấy danh sách user của chuyên viên và quản lý
		specialist_users = User.objects.filter(specialist__in=specialists)
		manager_users = User.objects.filter(manager__in=managers)

		# Kết hợp danh sách user của chuyên viên và quản lý thành một queryset chung
		combined_users = specialist_users | manager_users

		# Sử dụng UserPagination để phân trang
		paginator = UserPagination()
		paginated_users = paginator.paginate_queryset(combined_users, request)

		# Sử dụng UserSerializer để serialize dữ liệu
		serializer = UserSerializer(paginated_users, many=True)

		# Trả về kết quả phân trang
		return paginator.get_paginated_response(serializer.data)

