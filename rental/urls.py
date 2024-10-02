from django.urls import path, include
from rest_framework import routers

from rental import views

router = routers.DefaultRouter()
router.register(prefix="rooms", viewset=views.RoomViewSet, basename="rooms")
router.register(prefix="beds", viewset=views.BedViewSet, basename="beds")
router.register(prefix="posts", viewset=views.PostViewSet, basename="posts")
router.register(prefix="rental-contacts", viewset=views.RentalContactViewSet, basename="rental-contacts")
router.register(prefix="bill-rental-contacts", viewset=views.BillRentalContactViewSet, basename="bill-rental-contacts")
router.register(prefix="violate-notices", viewset=views.ViolateNoticeViewSet, basename="violate-notices")
router.register(prefix="electricity-and-water-bills", viewset=views.ElectricityAndWaterBillsViewSet, basename="electricity-and-water-bills")
router.register(prefix="statistics", viewset=views.StatisticsViewSet, basename="statistics")

urlpatterns = [path("", include(router.urls))]
