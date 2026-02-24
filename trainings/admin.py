from django.contrib import admin
from .models import TrainingSession, Attendance, DrillCatalog, TrainingDrill, DrillScore

admin.site.register(TrainingSession)
admin.site.register(Attendance)
admin.site.register(DrillCatalog)
admin.site.register(TrainingDrill)
admin.site.register(DrillScore)