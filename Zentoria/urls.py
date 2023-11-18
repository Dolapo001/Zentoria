"""
URL configuration for Zentoria project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

#from accounts.views import GoogleAuthView

schema_view = swagger_get_schema_view(
    openapi.Info(
        title="Zentoria_Api",
        default_version="1.0.0",
        description="API documentation of Zentoria",
    ),
    public=True
)

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('api-auth/', include("rest_framework.urls")),
    #path('auth/', include('social_django.urls', namespace='social')),
    path("api/v1/", include("Products.urls")),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/',
         include([
            path('swagger/schema/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema'),
         ])
         ),
    #path('api/v1/auth/google/', GoogleAuthView.as_view(), name='google-auth'),

]
