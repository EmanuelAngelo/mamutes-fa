from rest_framework.routers import DefaultRouter
from .views import TrainingSessionViewSet, DrillCatalogViewSet, TrainingDrillViewSet, DrillScoreViewSet

router = DefaultRouter()
router.register(r"", TrainingSessionViewSet, basename="trainings")
router.register(r"catalog", DrillCatalogViewSet, basename="drill-catalog")
router.register(r"drills", TrainingDrillViewSet, basename="training-drills")
router.register(r"scores", DrillScoreViewSet, basename="drill-scores")

urlpatterns = router.urls