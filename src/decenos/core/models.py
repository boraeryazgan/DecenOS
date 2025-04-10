from django.db import models
from django.utils import timezone
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
    state = models.CharField(max_length=20, choices=ProcessState.choices, default=ProcessState.NEW)
    memory_required = models.IntegerField(default=0)  
    created_at = models.DateTimeField(default=timezone.now)

    class ProcessType(models.TextChoices):
        DEFAULT = 'DEFAULT'
        HACKER = 'HACKER'
        MINER = 'MINER'
        VALIDATOR = 'VALIDATOR'

    process_type = models.CharField(max_length=20, choices=ProcessType.choices, default=ProcessType.DEFAULT)

    def __str__(self):
        return f"{self.name} ({self.get_state_display()})"
