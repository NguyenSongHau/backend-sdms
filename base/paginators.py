from rest_framework import pagination


class UserPagination(pagination.PageNumberPagination):
	page_size = 20


class RoomPaginators(pagination.PageNumberPagination):
	page_size = 10


class PostPaginators(pagination.PageNumberPagination):
	page_size = 10


class BedPaginators(pagination.PageNumberPagination):
	page_size = 10


class CommentPaginators(pagination.PageNumberPagination):
	page_size = 10


class RentalContactPaginators(pagination.PageNumberPagination):
	page_size = 10


class BillRentalContactPaginators(pagination.PageNumberPagination):
	page_size = 10


class ViolateNoticePaginators(pagination.PageNumberPagination):
	page_size = 10


class ElectricityAndWaterBillsPaginators(pagination.PageNumberPagination):
	page_size = 10
