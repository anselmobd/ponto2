from django.contrib.auth import views as auth_views
from django.urls import include, path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from ponto2.admin import admin
from ponto2.views import index


urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('bordado/', include('bordado.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Autenticação
    path(
        'encerrar/',
        auth_views.LogoutView.as_view(next_page="/"),
        name='encerrar',
    ),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name="layout/login.html"),
        name='login_p',
    ),
]
