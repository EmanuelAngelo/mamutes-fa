from rest_framework.routers import DefaultRouter

from .views import SavingsGoalViewSet

router = DefaultRouter()
router.register(r"goals", SavingsGoalViewSet, basename="goals")

urlpatterns = router.urls
