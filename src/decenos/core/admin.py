from django.contrib import admin
from .models import Process, File, Directory

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('pid', 'name', 'owner', 'state', 'process_type', 'memory_required', 'created_at')
    list_filter = ('state', 'process_type')
    search_fields = ('name', 'owner__username')

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'directory', 'owner', 'size', 'is_encrypted', 'created_at')
    list_filter = ('is_encrypted',)
    search_fields = ('name', 'owner__username')

@admin.register(Directory)
class DirectoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')
