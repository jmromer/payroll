from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(
    r'payroll-report',
    views.PayrollReportViewSet,
    basename='payroll-report',
)

router.register(
    r'time-entries',
    views.TimeEntryViewSet,
    basename='time-entries',
)

urlpatterns = [
    path('', include(router.urls)),
]
