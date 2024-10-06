from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework import viewsets, generics, parsers, status, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from base import perms, paginators
from interacts import serializers as interacts_serializers
from rental import serializers as rental_serializers
from rental.models import Room, Bed, Post, RentalContact, ViolateNotice, ElectricityAndWaterBills, BillRentalContact
from users.models import User
from utils.constants import PRICE_OF_ELECTRICITY, PRICE_OF_WATER
from utils.factory import to_float, update_status


class RoomViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
	queryset = Room.objects.filter(is_active=True).order_by("-id")
	serializer_class = rental_serializers.RoomSerializer
	pagination_class = paginators.RoomPaginators
	parser_classes = [parsers.MultiPartParser, ]

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			name = self.request.query_params.get("name")
			queryset = queryset.filter(name__icontains=name) if name else queryset

		return queryset

	def get_permissions(self):
		if self.action in ["list", "retrieve"]:
			return [permissions.AllowAny()]

		return [perms.IsSpecialist()]

	def partial_update(self, request, pk=None):
		serializer = self.serializer_class(instance=self.get_object(), data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data=serializer.data, status=status.HTTP_200_OK)


class PostViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
	queryset = Post.objects.select_related("room").filter(is_active=True).order_by("-id")
	serializer_class = rental_serializers.PostSerializer
	pagination_class = paginators.PostPaginators
	parser_classes = [parsers.MultiPartParser, ]

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			name = self.request.query_params.get("name")
			queryset = queryset.filter(name__icontains=name) if name else queryset

			room_type = self.request.query_params.get("type")
			queryset = queryset.filter(room__type=room_type.upper()) if room_type else queryset

		queryset = queryset.prefetch_related("comments") if self.action.__eq__("comments") else queryset

		return queryset

	def get_permissions(self):
		if self.action in ["create", "partial_update", "destroy"]:
			return [perms.IsSpecialist()]

		if self.action in ["comments"] and self.request.method.__eq__("POST"):
			return [permissions.IsAuthenticated()]

		return [permissions.AllowAny()]

	def get_serializer_class(self):
		if self.request.user.is_authenticated:
			return rental_serializers.AuthenticatedPostSerializer

		return self.serializer_class

	@action(methods=["get", "post"], detail=True, url_path="comments")
	def comments(self, request, pk=None):
		if request.method.__eq__("POST"):
			content = request.data.get("content")
			comment = self.get_object().comments.create(content=content, user=request.user)
			serializer = interacts_serializers.CommentSerializer(comment)

			return Response(data=serializer.data, status=status.HTTP_201_CREATED)

		# Method GET
		comments = self.get_object().comments.select_related("user").order_by("-id")
		paginator = paginators.CommentPaginators()
		page = paginator.paginate_queryset(queryset=comments, request=request)
		if page is not None:
			serializer = interacts_serializers.CommentSerializer(page, many=True)
			return paginator.get_paginated_response(serializer.data)

		serializer = interacts_serializers.CommentSerializer(comments, many=True)
		return Response(data=serializer.data, status=status.HTTP_200_OK)

	@action(methods=["post"], detail=True, url_path="like")
	def like_activity(self, request, pk=None):
		like, created = self.get_object().likes.get_or_create(user=request.user)
		if not created:
			like.is_active = not like.is_active
			like.save()

		serializer = self.get_serializer_class()(self.get_object(), context={"request": request})
		return Response(data=serializer.data, status=status.HTTP_200_OK)

	def partial_update(self, request, pk=None):
		serializer = self.serializer_class(instance=self.get_object(), data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data=serializer.data, status=status.HTTP_200_OK)


class BedViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
	queryset = Bed.objects.filter(is_active=True).order_by("-id")
	serializer_class = rental_serializers.BedSerializer
	pagination_class = paginators.BedPaginators
	parser_classes = [parsers.MultiPartParser, ]

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			name = self.request.query_params.get("name")
			queryset = queryset.filter(name__icontains=name) if name else queryset

		return queryset

	def get_permissions(self):
		if self.action in ["create", "partial_update", "destroy"]:
			return [perms.IsSpecialist()]

		if self.action in ["rent_bed"]:
			return [perms.IsStudent()]

		return [permissions.AllowAny()]

	@action(methods=["post"], detail=True, url_path="rent")
	def rent_bed(self, request, pk=None):
		time_rental = request.data.get("time_rental")
		student = request.user.student
		bed = self.get_object()

		existing_rental_contact = RentalContact.objects.filter(bed=bed, student=student).exists()
		if existing_rental_contact:
			return Response(data={"message": "Giường đã được thuê trước đó."}, status=status.HTTP_400_BAD_REQUEST)

		if request.user.gender == User.Gender.UNKNOWN:
			return Response(data={"message": "Vui lòng cập nhật giới tính!"}, status=status.HTTP_400_BAD_REQUEST)

		if request.user.gender != bed.room.room_for:
			return Response(data={"message": "Giường không phù hợp với giới tính của bạn!"}, status=status.HTTP_400_BAD_REQUEST)

		rental_contact = student.rental_contacts.create(bed=bed, time_rental=time_rental)

		serializer = rental_serializers.RentalContactSerializer(rental_contact)
		return Response(data=serializer.data, status=status.HTTP_201_CREATED)

	def partial_update(self, request, pk=None):
		serializer = self.serializer_class(instance=self.get_object(), data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data=serializer.data, status=status.HTTP_200_OK)


class RentalContactViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
	queryset = RentalContact.objects.select_related("student", "bed").filter(is_active=True).order_by("-id")
	serializer_class = rental_serializers.RentalContactSerializer
	pagination_class = paginators.RentalContactPaginators

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			rental_number = self.request.query_params.get("rental_number")
			queryset = queryset.filter(rental_number=rental_number) if rental_number else queryset

			rental_status = self.request.query_params.get("status")
			queryset = queryset.filter(status=rental_status.upper()) if rental_status else queryset

			student_id = self.request.query_params.get("student_id")
			queryset = queryset.filter(student_id=student_id) if student_id else queryset

			bed_id = self.request.query_params.get("bed_id")
			queryset = queryset.filter(bed_id=bed_id) if bed_id else queryset

		return queryset

	def get_permissions(self):
		if self.action in ["cancel"]:
			return [perms.IsStudent()]

		return [perms.IsSpecialist()]

	@action(methods=["post"], detail=True, url_path="cancel")
	def cancel(self, request, pk=None):
		rental_contact = self.get_object()
		return update_status(rental_contact=rental_contact, new_status=RentalContact.Status.CANCEL, message="Hủy hồ sơ thành công.")

	@action(methods=["post"], detail=True, url_path="confirm")
	def confirm(self, request, pk=None):
		rental_contact = self.get_object()
		specialist = request.user.specialist

		if rental_contact.status != RentalContact.Status.PROCESSING:
			return Response(data={"message": "Duyệt hồ sơ thành công."}, status=status.HTTP_400_BAD_REQUEST)

		rental_contact.status = RentalContact.Status.SUCCESS
		rental_contact.save()

		serializer = self.get_serializer_class()(rental_contact)

		return Response(data=serializer.data, status=status.HTTP_200_OK)

	@action(methods=["post"], detail=True, url_path="reject")
	def reject(self, request, pk=None):
		rental_contact = self.get_object()
		return update_status(rental_contact=rental_contact, new_status=RentalContact.Status.FAIL, message="Đã từ chối hồ sơ.")


class BillRentalContactViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
	queryset = BillRentalContact.objects.select_related("student", "specialist", "rental_contact").filter(is_active=True).order_by("-id")
	serializer_class = rental_serializers.BillRentalContactSerializer
	pagination_class = paginators.BillRentalContactPaginators
	permission_classes = [perms.IsSpecialist]

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			bill_number = self.request.query_params.get("bill_number")
			queryset = queryset.filter(bill_number=bill_number) if bill_number else queryset

			rental_status = self.request.query_params.get("status")
			queryset = queryset.filter(status=rental_status.upper()) if rental_status else queryset

			student_id = self.request.query_params.get("student_id")
			queryset = queryset.filter(student_id=student_id) if student_id else queryset

			specialist_id = self.request.query_params.get("specialist")
			queryset = queryset.filter(specialist_id=specialist_id) if specialist_id else queryset

			rental_contact_id = self.request.query_params.get("rental_contact")
			queryset = queryset.filter(rental_contact_id=rental_contact_id) if rental_contact_id else queryset

		return queryset

	def create(self, request, *args, **kwargs):
		rental_number = request.data.get("rental_number")

		rental_contact = get_object_or_404(queryset=RentalContact, rental_number=rental_number)

		if rental_contact.status != RentalContact.Status.SUCCESS:
			return Response(data={"message": "Hồ sơ chưa được xác nhận."}, status=status.HTTP_400_BAD_REQUEST)

		bill = BillRentalContact.objects.create(
			student=rental_contact.student,
			specialist=request.user.specialist,
			rental_contact=rental_contact,
			total=rental_contact.bed.price,
		)

		serializer = self.serializer_class(bill)

		return Response(data=serializer.data, status=status.HTTP_201_CREATED)

	def partial_update(self, request, pk=None):
		bill = self.get_object()
		
		if bill.status == BillRentalContact.Status.PAID:
			return Response(data={"message": "Hóa đơn đã được thanh toán."}, status=status.HTTP_400_BAD_REQUEST)

		serializer = self.serializer_class(instance=bill, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data=serializer.data, status=status.HTTP_200_OK)


class ViolateNoticeViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
	queryset = ViolateNotice.objects.select_related("room", "manager").filter(is_active=True).order_by("-id")
	serializer_class = rental_serializers.ViolateNoticeSerializer
	pagination_class = paginators.ViolateNoticePaginators

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			room_id = self.request.query_params.get("room_id")
			queryset = queryset.filter(room_id=room_id) if room_id else queryset

			manager_id = self.request.query_params.get("manager_id")
			queryset = queryset.filter(manager_id=manager_id) if manager_id else queryset

		return queryset

	def get_permissions(self):
		if self.action in ["create", "partial_update", "destroy"]:
			return [perms.IsManager()]

		return [permissions.AllowAny()]

	def create(self, request, *args, **kwargs):
		room_id = request.data.get("room_id")
		room = get_object_or_404(queryset=Room, id=room_id)
		description = request.data.get("description")

		violate_notice = room.violate_notices.create(description=description, manager=request.user.manager)
		serializer = self.serializer_class(violate_notice)

		return Response(data=serializer.data, status=status.HTTP_201_CREATED)

	def partial_update(self, request, pk=None):
		serializer = self.serializer_class(instance=self.get_object(), data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data=serializer.data, status=status.HTTP_200_OK)


class ElectricityAndWaterBillsViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveAPIView):
	queryset = ElectricityAndWaterBills.objects.select_related("room", "manager").filter(is_active=True).order_by("-id")
	serializer_class = rental_serializers.ElectricityAndWaterBillsSerializer
	pagination_class = paginators.ElectricityAndWaterBillsPaginators

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			room_id = self.request.query_params.get("room_id")
			queryset = queryset.filter(room_id=room_id) if room_id else queryset

			manager_id = self.request.query_params.get("manager_id")
			queryset = queryset.filter(manager_id=manager_id) if manager_id else queryset

		return queryset

	def get_permissions(self):
		if self.action in ["create"]:
			return [perms.IsManager()]

		return [permissions.AllowAny()]

	def create(self, request, *args, **kwargs):
		room_id = request.data.get("room_id")
		room = get_object_or_404(queryset=Room, id=room_id)
		electricity = request.data.get("electricity")
		water = request.data.get("water")

		electricity = to_float(electricity)
		water = to_float(water)
		total_amount = electricity * PRICE_OF_ELECTRICITY + water * PRICE_OF_WATER

		electricity_and_water_bills = room.electricity_and_water_bills.create(
			total_electricity=electricity,
			total_cubic_meters_water=water,
			total_amount=total_amount,
			manager=request.user.manager
		)
		serializer = self.serializer_class(electricity_and_water_bills)

		return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class StatisticsViewSet(viewsets.ViewSet):
	permission_classes = [perms.IsSpecialist]

	@action(detail=False, methods=['get'], url_path='rentals')
	def get_successful_rentals_by_month(self, request):
		year = request.query_params.get("year")
		month = request.query_params.get("month")
		rentals = RentalContact.objects.filter(status=RentalContact.Status.SUCCESS)

		if year and month:
			rentals = rentals.filter(created_date__year=year, created_date__month=month)

		rentals = rentals.annotate(month=TruncMonth("created_date")).values("month").annotate(count=Count("id")).order_by("month")

		formatted_rentals = []
		for rental in rentals:
			formatted_month = rental["month"].strftime("%d-%m-%Y")
			formatted_rentals.append({
				"date": formatted_month,
				"count": rental["count"]
			})

		return Response(data=formatted_rentals, status=status.HTTP_200_OK)
