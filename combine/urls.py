from rest_framework.routers import DefaultRouter
from .views import TestTypeViewSet, AssessmentEventViewSet, AssessmentResultViewSet

router = DefaultRouter()
router.register(r"tests", TestTypeViewSet, basename="test-types")
router.register(r"events", AssessmentEventViewSet, basename="assessment-events")
router.register(r"results", AssessmentResultViewSet, basename="assessment-results")

urlpatterns = router.urls