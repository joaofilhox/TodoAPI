from django.urls import path
from . import views


urlpatterns = [
    path("tasks/", views.TaskView.as_view()),  
    path('tasks/import/', views.ImportTasksView.as_view(),),
    path("tasks/<int:pk>/", views.TaskUpdateDeleteView.as_view()),  
]