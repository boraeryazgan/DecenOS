from django.shortcuts import render
from .scheduler import update_tamagotchi
import time
import threading
from django.http import JsonResponse

from .models import Process, File, Directory
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from .os import DecenOS


# Create your views here.
QUANTUM = 1  

# Initialize OS instance lazily
_os_instance = None

def get_os_instance():
    global _os_instance
    if _os_instance is None:
        _os_instance = DecenOS()
    return _os_instance

@csrf_exempt
def create_process(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        process = Process.objects.create(
            name=data.get('name', 'Unnamed'),
            memory_required=data.get('memory_required', 0),
            process_type=data.get('process_type', 'DEFAULT'),
            state=Process.ProcessState.READY
        )
        return JsonResponse({'message': 'Process created', 'pid': process.pid})

def list_processes(request):
    processes = Process.objects.all().order_by('created_at')
    return JsonResponse([{
        'pid': p.pid,
        'name': p.name,
        'state': p.state,
        'memory': p.memory_required,
        'type': p.process_type,
        'created_at': p.created_at,
    } for p in processes], safe=False)

@csrf_exempt
def terminate_process(request, pid):
    try:
        process = Process.objects.get(pid=pid)
        process.state = Process.ProcessState.TERMINATED
        process.save()
        return JsonResponse({'message': f'Process {pid} terminated'})
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)

# Round Robin Scheduler (çok basit simülasyon)
def run_scheduler(request):
    ready_queue = Process.objects.filter(state=Process.ProcessState.READY).order_by('created_at')

    if not ready_queue.exists():
        return JsonResponse({'message': 'No READY processes in queue'})

    current_process = ready_queue.first()
    current_process.state = Process.ProcessState.RUNNING
    current_process.save()

    current_process.state = Process.ProcessState.READY
    current_process.save()

    return JsonResponse({'message': f'Process {current_process.pid} ran for {QUANTUM}s (quantum)'})

@csrf_exempt
def allocate_memory(request, pid):
    try:
        process = Process.objects.get(pid=pid)
        num_pages = int(request.GET.get('num_pages', 0)) 
        process.allocate_pages(num_pages)
        return JsonResponse({'message': f'{num_pages} pages allocated to Process {pid}'})
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)

@csrf_exempt
def free_memory(request, pid):
    try:
        process = Process.objects.get(pid=pid)
        process.free_pages()
        return JsonResponse({'message': f'Memory freed for Process {pid}'})
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)

# Global Lock ve Queue
queue = []
queue_lock = threading.Lock()
queue_condition = threading.Condition(queue_lock)
stop_event = threading.Event()
# Producer Thread
def producer():
    while True:
        # Yeni Process üretiyoruz
        process = Process.objects.create(name="Process", memory_required=100, process_type="DEFAULT", state=Process.ProcessState.READY)
        print(f"Producer: Created Process {process.pid}")
        
        with queue_condition:
            queue.append(process)
            queue_condition.notify_all()  # Consumer'a bildirim gönder
        
        time.sleep(2)  # Her 2 saniyede bir yeni process üretir

# Consumer Thread
def consumer():
    while True:
        with queue_condition:
            # Kuyruk boşsa bekler
            while not queue:
                queue_condition.wait()
            
            process = queue.pop(0)  # Kuyruktan process alır
            print(f"Consumer: Processing Process {process.pid}")
            
            # Process'in durumunu RUNNING yap
            process.state = Process.ProcessState.RUNNING
            process.save()
            
            time.sleep(3)  # Process'i işleme süresi (simülasyon)

@csrf_exempt
def start_concurrency(request):
    # Producer ve Consumer thread'lerini başlatıyoruz
    producer_thread = threading.Thread(target=producer)
    consumer_thread = threading.Thread(target=consumer)
    
    producer_thread.daemon = True  # Program sonlandığında thread'lerin kapanmasını sağlar
    consumer_thread.daemon = True

    producer_thread.start()
    consumer_thread.start()

    return JsonResponse({'message': 'Producer-Consumer simulation started'})
@csrf_exempt
def stop_concurrency(request):
    stop_event.set()  
    return JsonResponse({'message': 'Producer-Consumer simulation stopped'})

@login_required
def dashboard(request):
    """Render the main dashboard"""
    update_tamagotchi()

    processes = Process.objects.exclude(state=Process.ProcessState.TERMINATED)
    directories = Directory.objects.filter(parent=None)
    files = File.objects.filter(directory=None)
    
    # Get system metrics
    system_status = get_os_instance().get_system_status()
    
    return render(request, 'core/dashboard.html', {
        'processes': processes,
        'directories': directories,
        'files': files,
        'current_path': [],
        'memory_usage': system_status['memory_usage'],
        'process_count': system_status['process_count'],
        'ready_queue_size': system_status['ready_queue_size'],
        'current_process': system_status['current_process'],
        'file_system_status': system_status['file_system_status'],
        'console_history': []
    })

@login_required
def process_status(request):
    """Return JSON Tamagotchi status for all processes"""
    data = list(
        Process.objects.values('pid', 'happiness', 'hunger', 'alive')
    )
    return JsonResponse(data, safe=False)

@login_required
def file_explorer(request, directory_id=None):
    """Render the file explorer for a specific directory"""
    if directory_id:
        current_dir = Directory.objects.get(id=directory_id)
        directories = current_dir.subdirectories.all()
        files = current_dir.files.all()
        current_path = []
        temp_dir = current_dir
        while temp_dir:
            current_path.insert(0, temp_dir)
            temp_dir = temp_dir.parent
    else:
        current_dir = None
        directories = Directory.objects.filter(parent=None)
        files = File.objects.filter(directory=None)
        current_path = []
    
    # Get system status
    system_status = get_os_instance().get_system_status()
    
    return render(request, 'core/dashboard.html', {
        'processes': Process.objects.all(),
        'directories': directories,
        'files': files,
        'current_path': current_path,
        'current_dir': current_dir,
        'memory_usage': system_status.get('memory_usage', 0),
        'process_count': system_status.get('process_count', 0),
        'ready_queue_size': system_status.get('ready_queue_size', 0),
        'current_process': system_status.get('current_process', 'None'),
        'file_system_status': system_status.get('file_system_status', {'total_files': 0, 'total_directories': 0}),
        'console_history': []
    })

# API Endpoints
@login_required
def api_process_list(request):
    """Get list of all processes"""
    processes = Process.objects.exclude(state=Process.ProcessState.TERMINATED)
    return JsonResponse({
        'processes': [{
            'pid': p.pid,
            'name': p.name,
            'owner': p.owner.username,
            'state': p.state,
            'process_type': p.process_type,
            'memory_required': p.memory_required
        } for p in processes]
    })

@login_required
def api_process_terminate(request, pid):
    """Terminate a process"""
    try:
        process = Process.objects.get(pid=pid)
        if process.owner != request.user:
            return JsonResponse({
                'success': False,
                'message': 'Permission denied: You can only terminate your own processes'
            }, status=403)
        
        # First update the process state
        process.update_state(Process.ProcessState.TERMINATED)
        
        # Then try to terminate through the OS instance
        success = get_os_instance().terminate_process(pid)
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Process {pid} terminated successfully',
                'pid': pid
            })
        return JsonResponse({
            'success': False,
            'message': f'Failed to terminate process {pid}',
            'pid': pid
        }, status=400)
    except Process.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': f'Process {pid} not found',
            'pid': pid
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error terminating process: {str(e)}',
            'pid': pid
        }, status=500)

@login_required
def api_process_create(request):
    """Create a new process"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            process = get_os_instance().create_process(
                name=data['name'],
                owner=request.user,
                memory_required=int(data.get('memory_required', 0)),
                process_type=data.get('process_type', 'DEFAULT')
            )
            if process:
                return JsonResponse({
                    'success': True,
                    'pid': process.pid,
                    'message': f'Process {process.name} created successfully'
                })
            return JsonResponse({
                'success': False,
                'message': 'Failed to create process'
            }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        except KeyError as e:
            return JsonResponse({
                'success': False,
                'message': f'Missing required field: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error creating process: {str(e)}'
            }, status=500)
    return JsonResponse({
        'success': False,
        'message': 'Method not allowed'
    }, status=405)

@login_required
def api_file_view(request, file_id):
    """Get file content"""
    try:
        file = File.objects.get(id=file_id)
        if not file.has_permission(request.user, 'read'):
            return JsonResponse({
                'success': False,
                'message': 'Permission denied'
            }, status=403)
        
        return JsonResponse({
            'success': True,
            'name': file.name,
            'size': file.size,
            'is_encrypted': file.is_encrypted,
            'content': file.content or '',
            'message': 'File content retrieved successfully'
        })
    except File.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'File not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error reading file: {str(e)}'
        }, status=500)

@login_required
def api_file_create(request):
    """Create a new file"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            directory_id = data.get('directory_id')
            
            # Get or create root directory
            root_directory = Directory.objects.filter(parent=None).first()
            if not root_directory:
                root_directory = Directory.objects.create(
                    name="root",
                    parent=None,
                    owner=request.user
                )
            
            # If directory_id is provided, use that directory instead of root
            if directory_id:
                try:
                    directory = Directory.objects.get(id=directory_id)
                except Directory.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Directory not found'
                    }, status=404)
            else:
                # Explicitly use root directory
                directory = root_directory
            
            # Create the file
            file = get_os_instance().file_system.create_file(
                name=data['name'],
                content=data.get('content', ''),
                directory=directory,
                owner=request.user,
                is_encrypted=data.get('is_encrypted', False)
            )
            
            if file:
                return JsonResponse({
                    'success': True,
                    'file_id': file.id,
                    'name': file.name,
                    'directory': file.directory.name,
                    'message': f'File {file.name} created successfully in {file.directory.name}'
                })
            return JsonResponse({
                'success': False,
                'message': 'Failed to create file'
            }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        except KeyError as e:
            return JsonResponse({
                'success': False,
                'message': f'Missing required field: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error creating file: {str(e)}'
            }, status=500)
    return JsonResponse({
        'success': False,
        'message': 'Method not allowed'
    }, status=405)

@login_required
def api_directory_create(request):
    """Create a new directory"""
    if request.method == 'POST':
        data = json.loads(request.body)
        parent = Directory.objects.get(id=data['parent_id']) if data.get('parent_id') else None
        directory = get_os_instance().file_system.create_directory(
            name=data['name'],
            parent=parent,
            owner=request.user
        )
        return JsonResponse({
            'success': True,
            'directory_id': directory.id
        })
    return JsonResponse({'success': False})

@login_required
def api_system_status(request):
    """Get current system status"""
    status = get_os_instance().get_system_status()
    return JsonResponse({
        'memory_usage': status['memory_usage'],
        'process_count': status['process_count'],
        'ready_queue_size': status['ready_queue_size'],
        'current_process': status['current_process'],
        'file_system_status': status['file_system_status']
    })