from django.urls import path
from .views import MyLatestTrainingView, MyDrillTrendsView, MyImprovementsView

urlpatterns = [
    path("my/latest-training/", MyLatestTrainingView.as_view()),
    path("my/drill-trends/", MyDrillTrendsView.as_view()),
    path("my/improvements/", MyImprovementsView.as_view()),
]