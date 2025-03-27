from rest_framework.routers import DefaultRouter
from .views import ReservationAdminViewSet

router = DefaultRouter()
router.register('', ReservationAdminViewSet, basename='user-reservation')

urlpatterns = router.urls