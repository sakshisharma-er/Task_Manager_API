from django.urls import path
from .views import *


urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<str:pk>/', TaskDetailView.as_view(), name='task-put-delete'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('tokenrefresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('taskfilterbycompleted/<str:completed>/<int:page_size>/<int:page_number>/', TaskfilterbyCompletedView.as_view(), name ='filter-by-completed'),

]
