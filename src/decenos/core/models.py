from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class Process(models.Model):
    class ProcessState(models.TextChoices):
        NEW = 'NEW'
        READY = 'READY'
        RUNNING = 'RUNNING'
        WAITING = 'WAITING'
        TERMINATED = 'TERMINATED'

    pid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processes')
    state = models.CharField(max_length=20, choices=ProcessState.choices, default=ProcessState.NEW)
    memory_required = models.IntegerField(default=0)  
    created_at = models.DateTimeField(default=timezone.now)
    last_run_time = models.DateTimeField(null=True, blank=True)
    quantum = models.IntegerField(default=100)  # Time quantum in milliseconds
    priority = models.IntegerField(default=0)  # For Round Robin, all processes have equal priority
    

    class ProcessType(models.TextChoices):
        DEFAULT = 'DEFAULT'
        HACKER = 'HACKER'
        MINER = 'MINER'
        VALIDATOR = 'VALIDATOR'

    process_type = models.CharField(max_length=20, choices=ProcessType.choices, default=ProcessType.DEFAULT)

    page_table = models.JSONField(default=list) 

    happiness = models.IntegerField(default=100)  
    hunger = models.IntegerField(default=0)      
    alive = models.BooleanField(default=True)


    def allocate_pages(self, num_pages):
        self.page_table = list(range(num_pages))  
        self.save()

    def free_pages(self):
        self.page_table = []
        self.save()

    def update_state(self, new_state):
        self.state = new_state
        if new_state == self.ProcessState.RUNNING:
            self.last_run_time = timezone.now()
        self.save()

    def __str__(self):
        return f"Process {self.pid} - {self.name} (Owner: {self.owner.username})"

class Directory(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subdirectories')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_directories')
    created_at = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'parent')

    def __str__(self):
        return self.get_full_path()

    def get_full_path(self):
        if self.parent:
            return f"{self.parent.get_full_path()}/{self.name}"
        return f"/{self.name}"

class File(models.Model):
    name = models.CharField(max_length=255)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, related_name='files')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_files')
    content = models.TextField(blank=True)
    size = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True)
    is_encrypted = models.BooleanField(default=False)
    permissions = models.JSONField(default=dict)  # Store user permissions

    class Meta:
        unique_together = ('name', 'directory')

    def __str__(self):
        return f"{self.directory.get_full_path()}/{self.name}"

    def get_full_path(self):
        return f"{self.directory.get_full_path()}/{self.name}"

    def has_permission(self, user, permission_type):
        if user == self.owner:
            return True
        return self.permissions.get(str(user.id), {}).get(permission_type, False)
