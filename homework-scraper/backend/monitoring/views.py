"""
Views for monitoring server logs and system status
"""
import subprocess
import os
import platform
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def run_command(command):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            'success': True,
            'output': result.stdout,
            'error': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Command timed out',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'returncode': -1
        }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_status(request):
    """Get system status information"""
    try:
        # Get system info
        system_info = {
            'hostname': platform.node(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'timestamp': datetime.now().isoformat(),
        }
        
        # Get uptime
        if platform.system() == 'Linux':
            uptime_result = run_command('uptime -p')
            system_info['uptime'] = uptime_result['output'].strip() if uptime_result['success'] else 'N/A'
            
            # Get memory info
            mem_result = run_command('free -h | grep Mem')
            system_info['memory'] = mem_result['output'].strip() if mem_result['success'] else 'N/A'
            
            # Get disk usage
            disk_result = run_command('df -h / | tail -1')
            system_info['disk'] = disk_result['output'].strip() if disk_result['success'] else 'N/A'
            
            # Get CPU usage
            cpu_result = run_command('top -bn1 | grep "Cpu(s)"')
            system_info['cpu'] = cpu_result['output'].strip() if cpu_result['success'] else 'N/A'
        
        return Response({
            'success': True,
            'system_info': system_info
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_running_services(request):
    """Get status of homework scraper services"""
    try:
        services = [
            'homework-scraper.service',
            'homework-scraper-celery.service',
            'homework-scraper-celery-beat.service',
        ]
        
        service_status = []
        
        for service in services:
            if platform.system() == 'Linux':
                # Check if service exists and get status
                status_cmd = f'systemctl is-active {service} 2>/dev/null || echo "not-found"'
                status_result = run_command(status_cmd)
                status = status_result['output'].strip()
                
                # Get service details if active
                if status == 'active':
                    details_cmd = f'systemctl status {service} --no-pager -l | head -20'
                    details_result = run_command(details_cmd)
                    details = details_result['output'] if details_result['success'] else ''
                else:
                    details = ''
                
                service_status.append({
                    'name': service,
                    'status': status,
                    'details': details
                })
            else:
                service_status.append({
                    'name': service,
                    'status': 'unavailable',
                    'details': 'Service monitoring only available on Linux'
                })
        
        return Response({
            'success': True,
            'services': service_status
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_application_logs(request):
    """Get application logs"""
    try:
        log_type = request.GET.get('type', 'django')
        lines = int(request.GET.get('lines', 100))
        
        log_files = {
            'django': '/var/log/homework-scraper/django.log',
            'celery': '/var/log/homework-scraper/celery.log',
            'celery-beat': '/var/log/homework-scraper/celery-beat.log',
            'nginx': '/var/log/nginx/homework-scraper-access.log',
            'nginx-error': '/var/log/nginx/homework-scraper-error.log',
        }
        
        log_file = log_files.get(log_type)
        
        if not log_file:
            return Response({
                'success': False,
                'error': f'Invalid log type: {log_type}'
            }, status=400)
        
        # Try to read the log file
        if os.path.exists(log_file):
            result = run_command(f'tail -n {lines} {log_file}')
            logs = result['output'] if result['success'] else result['error']
        else:
            # Fallback: try to get logs from journalctl
            if log_type in ['django', 'celery', 'celery-beat']:
                service_name = f'homework-scraper-{log_type}.service' if log_type != 'django' else 'homework-scraper.service'
                result = run_command(f'journalctl -u {service_name} -n {lines} --no-pager')
                logs = result['output'] if result['success'] else f'Log file not found: {log_file}'
            else:
                logs = f'Log file not found: {log_file}'
        
        return Response({
            'success': True,
            'log_type': log_type,
            'logs': logs,
            'lines_requested': lines
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_errors(request):
    """Get recent errors from logs"""
    try:
        lines = int(request.GET.get('lines', 50))
        
        # Search for errors in Django logs
        if platform.system() == 'Linux':
            error_cmd = f'journalctl -u homework-scraper.service -n {lines * 10} --no-pager | grep -i "error\\|exception\\|critical" | tail -n {lines}'
            result = run_command(error_cmd)
            errors = result['output'] if result['success'] else 'No errors found or unable to access logs'
        else:
            errors = 'Error monitoring only available on Linux'
        
        return Response({
            'success': True,
            'errors': errors,
            'lines_requested': lines
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_process_info(request):
    """Get information about running Python processes"""
    try:
        if platform.system() == 'Linux':
            # Get Python processes
            ps_cmd = 'ps aux | grep -E "python|celery|django" | grep -v grep'
            result = run_command(ps_cmd)
            processes = result['output'] if result['success'] else 'Unable to get process info'
        else:
            processes = 'Process monitoring only available on Linux'
        
        return Response({
            'success': True,
            'processes': processes
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def monitoring_info(request):
    """Get available monitoring endpoints"""
    base_url = request.build_absolute_uri('/api/monitoring/')
    
    return Response({
        'success': True,
        'message': 'Server Monitoring API',
        'endpoints': {
            'system_status': f'{base_url}system-status/',
            'running_services': f'{base_url}services/',
            'application_logs': f'{base_url}logs/?type=django&lines=100',
            'recent_errors': f'{base_url}errors/',
            'process_info': f'{base_url}processes/',
        },
        'log_types': ['django', 'celery', 'celery-beat', 'nginx', 'nginx-error'],
        'note': 'All endpoints require authentication'
    })
