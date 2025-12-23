from django.urls import path
from . import views

urlpatterns = [
    path('tap-production/', views.tap_production, name='tap_production'),
    path('grade-distribution/', views.grade_distribution, name='grade_distribution'),
    path('health-breakdown/', views.health_breakdown, name='health_breakdown'),
    path('downtime/summary/', views.downtime_summary, name='downtime_summary'),
    path('downtime/reasons/', views.downtime_reasons, name='downtime_reasons'),
]
