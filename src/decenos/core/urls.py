# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_process, name='create_process'),
    path('list/', views.list_processes, name='list_processes'),
    path('terminate/<int:pid>/', views.terminate_process, name='terminate_process'),
    path('run/', views.run_scheduler, name='run_scheduler'),
]
