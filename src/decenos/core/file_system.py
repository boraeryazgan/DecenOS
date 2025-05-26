import threading
from queue import Queue
from django.utils import timezone
from .models import File, Directory

class FileSystemManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.file_locks = {}  # Store locks for individual files
        self.condition = threading.Condition()
        self.buffer_size = 10  # For producer-consumer simulation
        self.buffer = Queue(maxsize=self.buffer_size)
        self.producer_thread = None
        self.consumer_thread = None
        self.is_running = False

    def create_directory(self, name, parent=None, owner=None):
        """Create a new directory"""
        with self.lock:
            directory = Directory.objects.create(
                name=name,
                parent=parent,
                owner=owner
            )
            return directory

    def create_file(self, name, content='', directory=None, owner=None, is_encrypted=False):
        """Create a new file"""
        try:
            # If no directory is provided, use root directory
            if directory is None:
                # Get the root directory (parent=None)
                root_directory = Directory.objects.filter(parent=None).first()
                if root_directory is None:
                    # Create root directory if it doesn't exist
                    root_directory = Directory.objects.create(
                        name="root",
                        parent=None,
                        owner=owner
                    )
                directory = root_directory
            
            # Create the file
            file = File.objects.create(
                name=name,
                content=content,
                directory=directory,
                owner=owner,
                size=len(content),
                is_encrypted=is_encrypted,
                permissions={}  # Default empty permissions
            )
            
            self.file_locks[file.id] = threading.Lock()
            return file
        except Exception as e:
            print(f"Error creating file: {str(e)}")
            return None

    def read_file(self, file_id, user):
        """Read file content with permission check"""
        with self.lock:
            try:
                file = File.objects.get(id=file_id)
                if not file.has_permission(user, 'read'):
                    raise PermissionError("No read permission")
                
                with self.file_locks[file.id]:
                    return file.content
            except File.DoesNotExist:
                raise FileNotFoundError("File not found")

    def write_file(self, file_id, content, user):
        """Write to file with permission check"""
        with self.lock:
            try:
                file = File.objects.get(id=file_id)
                if not file.has_permission(user, 'write'):
                    raise PermissionError("No write permission")
                
                with self.file_locks[file.id]:
                    file.content = content
                    file.size = len(content)
                    file.last_modified = timezone.now()
                    file.save()
            except File.DoesNotExist:
                raise FileNotFoundError("File not found")

    def delete_file(self, file_id, user):
        """Delete a file with permission check"""
        with self.lock:
            try:
                file = File.objects.get(id=file_id)
                if not file.has_permission(user, 'delete'):
                    raise PermissionError("No delete permission")
                
                with self.file_locks[file.id]:
                    file.delete()
                    del self.file_locks[file.id]
            except File.DoesNotExist:
                raise FileNotFoundError("File not found")

    def set_permissions(self, file_id, user, permissions):
        """Set file permissions"""
        with self.lock:
            try:
                file = File.objects.get(id=file_id)
                if file.owner != user:
                    raise PermissionError("Only owner can set permissions")
                
                file.permissions = permissions
                file.save()
            except File.DoesNotExist:
                raise FileNotFoundError("File not found")

    # Producer-Consumer simulation for file operations
    def start_file_operations(self):
        """Start producer-consumer threads for file operations"""
        self.is_running = True
        self.producer_thread = threading.Thread(target=self._producer)
        self.consumer_thread = threading.Thread(target=self._consumer)
        self.producer_thread.start()
        self.consumer_thread.start()

    def stop_file_operations(self):
        """Stop producer-consumer threads"""
        self.is_running = False
        with self.condition:
            self.condition.notify_all()
        if self.producer_thread:
            self.producer_thread.join()
        if self.consumer_thread:
            self.consumer_thread.join()

    def _producer(self):
        """Simulate file operation producer"""
        while self.is_running:
            with self.condition:
                while self.buffer.full():
                    self.condition.wait()
                # Simulate producing file operations
                self.buffer.put("file_operation")
                self.condition.notify()

    def _consumer(self):
        """Simulate file operation consumer"""
        while self.is_running:
            with self.condition:
                while self.buffer.empty():
                    self.condition.wait()
                # Simulate consuming file operations
                operation = self.buffer.get()
                self.condition.notify()
                # Process the operation
                print(f"Processing operation: {operation}")

    def search_files(self, query, user):
        """Search files by name or content"""
        with self.lock:
            files = File.objects.filter(
                name__icontains=query,
                permissions__has_key=str(user.id)
            )
            return list(files)

    def get_directory_contents(self, directory):
        """Get contents of a directory"""
        with self.lock:
            return {
                'files': list(directory.files.all()),
                'subdirectories': list(directory.subdirectories.all())
            } 