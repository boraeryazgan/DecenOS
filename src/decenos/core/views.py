from django.shortcuts import render
import time
import threading
from django.http import JsonResponse
from .models import Process
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.
QUANTUM = 1  

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