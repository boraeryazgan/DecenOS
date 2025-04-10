from django.shortcuts import render
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

    # Simüle çalışıyor gibi yapalım (quantum kadar çalıştırıp kuyruğun sonuna atalım)
    current_process.state = Process.ProcessState.READY
    current_process.save()

    return JsonResponse({'message': f'Process {current_process.pid} ran for {QUANTUM}s (quantum)'})
