from .models import Process

class MemoryManager:
    def __init__(self, total_memory=1024, page_size=4):  # Default: 1024MB total, 4MB pages
        self.total_memory = total_memory
        self.page_size = page_size
        self.total_pages = total_memory // page_size
        self.free_pages = list(range(self.total_pages))
        self.allocated_pages = {}  # pid -> [page_numbers]

    def allocate_memory(self, process, memory_required):
        """Allocate memory for a process using paging"""
        if memory_required <= 0:
            return False

        # Calculate number of pages needed
        pages_needed = (memory_required + self.page_size - 1) // self.page_size

        # Check if enough free pages are available
        if len(self.free_pages) < pages_needed:
            return False

        # Allocate pages
        allocated = self.free_pages[:pages_needed]
        self.free_pages = self.free_pages[pages_needed:]
        self.allocated_pages[process.pid] = allocated
        process.allocate_pages(len(allocated))
        return True

    def free_memory(self, process):
        """Free memory allocated to a process"""
        if process.pid in self.allocated_pages:
            pages = self.allocated_pages[process.pid]
            self.free_pages.extend(pages)
            self.free_pages.sort()  # Keep pages in order
            del self.allocated_pages[process.pid]
            process.free_pages()
            return True
        return False

    def get_allocated_memory(self, process):
        """Get the amount of memory allocated to a process"""
        if process.pid in self.allocated_pages:
            return len(self.allocated_pages[process.pid]) * self.page_size
        return 0

    def get_free_memory(self):
        """Get the amount of free memory"""
        return len(self.free_pages) * self.page_size

    def get_memory_usage(self):
        """Get memory usage statistics"""
        total_allocated = sum(len(pages) for pages in self.allocated_pages.values())
        return {
            'total_memory': self.total_memory,
            'total_pages': self.total_pages,
            'free_pages': len(self.free_pages),
            'allocated_pages': total_allocated,
            'page_size': self.page_size
        } 