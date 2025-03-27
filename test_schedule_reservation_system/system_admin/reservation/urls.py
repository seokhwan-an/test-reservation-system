from rest_framework.routers import DefaultRouter
from .views import ReservationAdminViewSet

router = DefaultRouter()
router.register('', ReservationAdminViewSet, basename='admin-reservation')

urlpatterns = router.urls