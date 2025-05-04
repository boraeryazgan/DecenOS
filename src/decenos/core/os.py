from django.utils import timezone
from .models import Process, File, Directory
from .process_manager import ProcessManager
from .memory_manager import MemoryManager
from .scheduler import Scheduler
from .file_system import FileSystemManager
import threading

class DecenOS:
    def __init__(self, total_memory=1024, page_size=4, quantum=100):
        self.process_manager = ProcessManager()
        self.memory_manager = MemoryManager(total_memory, page_size)
        self.scheduler = Scheduler(quantum)
        self.file_system = FileSystemManager()
        self.is_running = False
        self.system_threads = []
        self.system_locks = {
            'process': threading.Lock(),
            'memory': threading.Lock(),
            'file_system': threading.Lock()
        }

    def start(self):
        """Start the OS"""
        self.is_running = True
        self._initialize_system_processes()
        self._start_system_threads()

    def stop(self):
        """Stop the OS"""
        self.is_running = False
        self._stop_system_threads()
        # Clean up all processes
        for process in self.process_manager.get_all_processes():
            self.process_manager.terminate_process(process.pid)

    def _start_system_threads(self):
        """Start system maintenance threads"""
        # Start file system operations
        self.file_system.start_file_operations()
        
        # Start memory management thread
        memory_thread = threading.Thread(target=self._memory_management_thread)
        memory_thread.daemon = True
        memory_thread.start()
        self.system_threads.append(memory_thread)

        # Start process monitoring thread
        process_thread = threading.Thread(target=self._process_monitoring_thread)
        process_thread.daemon = True
        process_thread.start()
        self.system_threads.append(process_thread)

    def _stop_system_threads(self):
        """Stop all system threads"""
        self.file_system.stop_file_operations()
        for thread in self.system_threads:
            thread.join(timeout=1.0)

    def _memory_management_thread(self):
        """Thread for periodic memory management tasks"""
        while self.is_running:
            with self.system_locks['memory']:
                # Perform memory cleanup and defragmentation
                self.memory_manager.get_memory_usage()
            timezone.sleep(60)  # Run every minute

    def _process_monitoring_thread(self):
        """Thread for monitoring process states"""
        while self.is_running:
            with self.system_locks['process']:
                # Check for dead processes
                for process in self.process_manager.get_all_processes():
                    if process.state == Process.ProcessState.TERMINATED:
                        self.process_manager.terminate_process(process.pid)
            timezone.sleep(30)  # Run every 30 seconds

    def create_process(self, name, owner, memory_required=0, process_type=Process.ProcessType.DEFAULT):
        """Create and start a new process with thread safety"""
        with self.system_locks['process']:
            # Create the process
            process = self.process_manager.create_process(
                name=name,
                owner=owner,
                memory_required=memory_required,
                process_type=process_type
            )

            # Allocate memory
            with self.system_locks['memory']:
                if not self.memory_manager.allocate_memory(process, memory_required):
                    self.process_manager.terminate_process(process.pid)
                    return None

            # Start the process
            self.process_manager.start_process(process.pid)
            return process

    def terminate_process(self, pid):
        """Terminate a process with thread safety"""
        with self.system_locks['process']:
            process = self.process_manager.get_process(pid)
            if process:
                with self.system_locks['memory']:
                    self.memory_manager.free_memory(process)
                return self.process_manager.terminate_process(pid)
            return False

    def get_process_info(self, pid):
        """Get detailed information about a process with thread safety"""
        with self.system_locks['process']:
            process = self.process_manager.get_process(pid)
            if not process:
                return None

            with self.system_locks['memory']:
                return {
                    'pid': process.pid,
                    'name': process.name,
                    'owner': process.owner.username,
                    'state': process.state,
                    'memory_allocated': self.memory_manager.get_allocated_memory(process),
                    'memory_required': process.memory_required,
                    'process_type': process.process_type,
                    'created_at': process.created_at,
                    'last_run_time': process.last_run_time
                }

    def get_system_status(self):
        """Get current system status with thread safety"""
        with self.system_locks['process']:
            with self.system_locks['memory']:
                with self.system_locks['file_system']:
                    return {
                        'is_running': self.is_running,
                        'memory_usage': self.memory_manager.get_memory_usage(),
                        'process_count': len(self.process_manager.get_all_processes()),
                        'ready_queue_size': len(self.scheduler.get_ready_queue()),
                        'current_process': self.scheduler.get_current_process().pid if self.scheduler.get_current_process() else None,
                        'file_system_status': {
                            'total_files': File.objects.count(),
                            'total_directories': Directory.objects.count()
                        }
                    }

    def _initialize_system_processes(self):
        """Initialize system processes"""
        # Create root directory
        root_dir = self.file_system.create_directory(name="root", owner=None)
        
        # Create system directories
        self.file_system.create_directory(name="system", parent=root_dir, owner=None)
        self.file_system.create_directory(name="users", parent=root_dir, owner=None)
        self.file_system.create_directory(name="temp", parent=root_dir, owner=None)

    def run_scheduler(self):
        """Run the scheduler to get the next process with thread safety"""
        if not self.is_running:
            return None
        with self.system_locks['process']:
            return self.scheduler.get_next_process() 