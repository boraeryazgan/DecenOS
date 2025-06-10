from django.utils import timezone
from .models import Process

class Scheduler:
    def __init__(self, quantum=100):
        self.quantum = quantum
        self.ready_queue = []
        self.current_process = None

    def add_process(self, process):
        if process.state == Process.ProcessState.READY:
            self.ready_queue.append(process)

    def get_next_process(self):
        if not self.ready_queue:
            return None

        next_proc = self.ready_queue.pop(0)
        if self.current_process and self.current_process.state == Process.ProcessState.RUNNING:
            self.current_process.update_state(Process.ProcessState.READY)
            self.ready_queue.append(self.current_process)

        next_proc.update_state(Process.ProcessState.RUNNING)
        self.current_process = next_proc
        return next_proc

    def remove_process(self, process):
        if process in self.ready_queue:
            self.ready_queue.remove(process)
        if self.current_process == process:
            self.current_process = None

    def get_ready_queue(self):
        return self.ready_queue

    def get_current_process(self):
        return self.current_process

    def has_process_expired_quantum(self):
        if not self.current_process or not self.current_process.last_run_time:
            return False
        elapsed = (timezone.now() - self.current_process.last_run_time).total_seconds() * 1000
        return elapsed >= self.quantum

def update_tamagotchi():
    for proc in Process.objects.filter(alive=True):
        if proc.state != Process.ProcessState.RUNNING:
            proc.hunger = min(100, proc.hunger + 5)
        else:
            proc.happiness = min(100, proc.happiness + 5)

        if proc.hunger > 80:
            proc.happiness = max(0, proc.happiness - 10)

        if proc.happiness <= 0:
            proc.alive = False
            proc.state = Process.ProcessState.TERMINATED

        proc.save()

def run_scheduler():
    update_tamagotchi()
