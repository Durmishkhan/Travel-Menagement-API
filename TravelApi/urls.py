from django.contrib import admin
from django.urls import path, include
from tours.views import UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/user/register/", UserViewSet.as_view({'post': 'register'}), name='register'),
    path("api/token/", TokenObtainPairView.as_view(), name='get_token'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path('api-auth/', include('rest_framework.urls')),
    path("api/", include('tours.urls'))
]
