from django.utils import timezone
from .models import Process
from .scheduler import Scheduler

class ProcessManager:
    def __init__(self):
        self.scheduler = Scheduler()
        self.processes = {}
        # Initialize processes from database
        self._initialize_processes()

    def _initialize_processes(self):
        """Initialize processes from the database"""
        for process in Process.objects.all():
            if process.state != Process.ProcessState.TERMINATED:
                self.processes[process.pid] = process
                if process.state == Process.ProcessState.READY:
                    self.scheduler.add_process(process)

    def create_process(self, name, owner, memory_required=0, process_type=Process.ProcessType.DEFAULT):
        """Create a new process"""
        process = Process.objects.create(
            name=name,
            owner=owner,
            memory_required=memory_required,
            process_type=process_type,
            state=Process.ProcessState.NEW
        )
        self.processes[process.pid] = process
        return process

    def start_process(self, pid):
        """Start a process by moving it to the ready queue"""
        if pid in self.processes:
            process = self.processes[pid]
            process.update_state(Process.ProcessState.READY)
            self.scheduler.add_process(process)
            return True
        return False

    def terminate_process(self, pid):
        """Terminate a process"""
        try:
            process = Process.objects.get(pid=pid)
            process.update_state(Process.ProcessState.TERMINATED)
            
            # Ensure process is in our manager
            if pid not in self.processes:
                self.processes[pid] = process
            
            # Remove from scheduler and manager
            self.scheduler.remove_process(process)
            process.free_pages()
            del self.processes[pid]
            
            return True
        except Process.DoesNotExist:
            return False
        except Exception as e:
            print(f"Error terminating process {pid}: {str(e)}")
            return False

    def get_process(self, pid):
        """Get a process by its PID"""
        if pid in self.processes:
            return self.processes[pid]
        try:
            process = Process.objects.get(pid=pid)
            if process.state != Process.ProcessState.TERMINATED:
                self.processes[pid] = process
            return process
        except Process.DoesNotExist:
            return None

    def get_all_processes(self):
        """Get all processes"""
        # Update our process list from database
        self._initialize_processes()
        return list(self.processes.values())

    def get_user_processes(self, user):
        """Get all processes owned by a specific user"""
        return [p for p in self.processes.values() if p.owner == user]

    def schedule(self):
        """Run the scheduler to get the next process"""
        if self.scheduler.has_process_expired_quantum():
            return self.scheduler.get_next_process()
        return self.scheduler.get_current_process() 