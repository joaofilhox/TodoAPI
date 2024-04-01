from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),  # URLs relacionadas a accounts
    path('api/', include('tasks.urls')),     # URLs relacionadas a tasks
    path('api-auth/', include('rest_framework.urls')),  # URLs para autenticação do Django REST Framework    
    path('api/schema/', SpectacularAPIView.as_view(), name="schema"), # URLs para a documentação Swagger
    path('api/docs/swagger/', SpectacularSwaggerView.as_view()),

]
