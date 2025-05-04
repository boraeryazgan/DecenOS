from django.utils import timezone
from .models import Process
from datetime import timedelta

class Scheduler:
    def __init__(self, quantum=100):  # Default quantum of 100ms
        self.quantum = quantum
        self.ready_queue = []
        self.current_process = None

    def add_process(self, process):
        """Add a new process to the ready queue"""
        if process.state == Process.ProcessState.READY:
            self.ready_queue.append(process)

    def get_next_process(self):
        """Get the next process to run using Round Robin scheduling"""
        if not self.ready_queue:
            return None

        # Get the next process from the queue
        next_process = self.ready_queue.pop(0)
        
        # If there's a current process, move it to the end of the queue
        if self.current_process and self.current_process.state == Process.ProcessState.RUNNING:
            self.current_process.update_state(Process.ProcessState.READY)
            self.ready_queue.append(self.current_process)

        # Update the next process's state
        next_process.update_state(Process.ProcessState.RUNNING)
        self.current_process = next_process
        return next_process

    def remove_process(self, process):
        """Remove a process from the scheduler"""
        if process in self.ready_queue:
            self.ready_queue.remove(process)
        if self.current_process == process:
            self.current_process = None

    def get_ready_queue(self):
        """Get the current ready queue"""
        return self.ready_queue

    def get_current_process(self):
        """Get the currently running process"""
        return self.current_process

    def has_process_expired_quantum(self):
        """Check if the current process has used up its quantum"""
        if not self.current_process or not self.current_process.last_run_time:
            return False
        
        time_elapsed = (timezone.now() - self.current_process.last_run_time).total_seconds() * 1000
        return time_elapsed >= self.quantum 