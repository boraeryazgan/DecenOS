# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard and File Explorer
    path('', views.dashboard, name='dashboard'),
    path('explorer/', views.file_explorer, name='file_explorer'),
    path('explorer/<int:directory_id>/', views.file_explorer, name='file_explorer_directory'),

    # API Endpoints
    path('api/processes/', views.api_process_list, name='api_process_list'),
    path('api/process/<int:pid>/terminate/', views.api_process_terminate, name='api_process_terminate'),
    path('api/process/create/', views.api_process_create, name='api_process_create'),
    path('api/file/<int:file_id>/', views.api_file_view, name='api_file_view'),
    path('api/file/create/', views.api_file_create, name='api_file_create'),
    path('api/directory/create/', views.api_directory_create, name='api_directory_create'),
    path('api/system/status/', views.api_system_status, name='api_system_status'),

    # Process Management
    path('create/', views.create_process, name='create_process'),
    path('list/', views.list_processes, name='list_processes'),
    path('terminate/<int:pid>/', views.terminate_process, name='terminate_process'),
    path('run_scheduler/', views.run_scheduler, name='run_scheduler'),
    path('allocate_memory/<int:pid>/', views.allocate_memory, name='allocate_memory'),
    path('free_memory/<int:pid>/', views.free_memory, name='free_memory'),
    path('start_concurrency/', views.start_concurrency, name='start_concurrency'),
    path('stop_concurrency/', views.stop_concurrency, name='stop_concurrency'),
]
