from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .services import RISCTokenValidator, RISCEventHandler
from .models import SecurityEvent

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def risc_receiver(request):
    """
    RISC Security Event Token receiver endpoint
    Receives JWT tokens from Google's RISC service
    """
    try:
        # Get JWT from request body
        content_type = request.headers.get('Content-Type', '')
        
        if 'application/secevent+jwt' in content_type:
            # Token sent as raw body
            token_string = request.body.decode('utf-8')
        elif 'application/json' in content_type:
            # Token sent in JSON wrapper
            data = json.loads(request.body)
            token_string = data.get('token') or data.get('SET')
        else:
            logger.error(f"Unsupported Content-Type: {content_type}")
            return JsonResponse({
                'err': 'invalid_request',
                'description': 'Content-Type must be application/secevent+jwt or application/json'
            }, status=400)
        
        if not token_string:
            return JsonResponse({
                'err': 'invalid_request',
                'description': 'No token found in request'
            }, status=400)
        
        # Validate token
        validator = RISCTokenValidator()
        try:
            decoded_token = validator.validate_token(token_string)
        except ValueError as e:
            error_msg = str(e)
            if 'already processed' in error_msg:
                # Duplicate event - return 202 Accepted
                logger.info(f"Duplicate event received: {error_msg}")
                return HttpResponse(status=202)
            else:
                logger.error(f"Token validation failed: {error_msg}")
                return JsonResponse({
                    'err': 'invalid_token',
                    'description': error_msg
                }, status=400)
        except Exception as e:
            logger.error(f"Token validation error: {e}", exc_info=True)
            return JsonResponse({
                'err': 'invalid_token',
                'description': str(e)
            }, status=400)
        
        # Process the event
        handler = RISCEventHandler()
        try:
            result = handler.process_event(decoded_token, token_string)
            
            if result['success']:
                logger.info(f"Successfully processed {result['event_type']}: {result['action']}")
                return HttpResponse(status=202)  # 202 Accepted
            else:
                logger.error(f"Event processing failed: {result['error']}")
                return JsonResponse({
                    'err': 'processing_error',
                    'description': result['error']
                }, status=500)
                
        except Exception as e:
            logger.error(f"Event processing error: {e}", exc_info=True)
            return JsonResponse({
                'err': 'processing_error',
                'description': str(e)
            }, status=500)
    
    except Exception as e:
        logger.error(f"RISC receiver error: {e}", exc_info=True)
        return JsonResponse({
            'err': 'internal_error',
            'description': str(e)
        }, status=500)


@require_http_methods(["GET"])
def risc_status(request):
    """
    Check RISC integration status
    Returns stats about received events
    """
    try:
        from .models import RISCConfiguration
        
        config = RISCConfiguration.objects.filter(is_active=True).first()
        
        if not config:
            return JsonResponse({
                'configured': False,
                'message': 'RISC not configured'
            })
        
        # Get event statistics
        total_events = SecurityEvent.objects.count()
        processed_events = SecurityEvent.objects.filter(processed=True).count()
        failed_events = SecurityEvent.objects.exclude(error_message='').count()
        
        recent_events = SecurityEvent.objects.order_by('-received_at')[:10].values(
            'event_type', 'google_email', 'received_at', 'processed', 'action_taken'
        )
        
        return JsonResponse({
            'configured': True,
            'enabled': config.stream_enabled,
            'receiver_endpoint': config.receiver_endpoint,
            'statistics': {
                'total_events': total_events,
                'processed_events': processed_events,
                'failed_events': failed_events
            },
            'recent_events': list(recent_events),
            'subscribed_events': config.get_subscribed_events()
        })
        
    except Exception as e:
        logger.error(f"Error getting RISC status: {e}", exc_info=True)
        return JsonResponse({
            'error': str(e)
        }, status=500)
