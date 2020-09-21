from django.urls import include, path

urlpatterns = [
    path('', include('reports.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
