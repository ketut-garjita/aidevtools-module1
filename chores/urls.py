from django.urls import path
from . import views

app_name = 'chores'

urlpatterns = [
    path('', views.chore_list, name='list'),
    path('new/', views.chore_create, name='create'),
    path('<int:pk>/complete/', views.chore_complete, name='complete'),
    path('<int:pk>/delete/', views.chore_delete, name='delete'),
]
