from django.contrib import admin
from django.urls import path, include, re_path
from tours.views import UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# swagger-ის დამატება
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Travel Management API",
        default_version='v1',
        description="API for managing trips, locations, and expenses",
        contact=openapi.Contact(email="you@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/user/register/", UserViewSet.as_view({'post': 'register'}), name='register'),
    path("api/token/", TokenObtainPairView.as_view(), name='get_token'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path('api-auth/', include('rest_framework.urls')),
    path("api/", include('tours.urls')),

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
