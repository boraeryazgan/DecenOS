# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_process, name='create_process'),
    path('list/', views.list_processes, name='list_processes'),
    path('terminate/<int:pid>/', views.terminate_process, name='terminate_process'),
    path('run_scheduler/', views.run_scheduler, name='run_scheduler'),
    path('allocate_memory/<int:pid>/', views.allocate_memory, name='allocate_memory'),
    path('free_memory/<int:pid>/', views.free_memory, name='free_memory'),
    path('start_concurrency/', views.start_concurrency, name='start_concurrency'),
    path('stop_concurrency/', views.stop_concurrency, name='stop_concurrency'),

]
