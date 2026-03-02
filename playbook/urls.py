from rest_framework.routers import DefaultRouter

from .views import PlayViewSet

router = DefaultRouter()
router.register(r"plays", PlayViewSet, basename="playbook-plays")

urlpatterns = router.urls
