import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .tasks import send_order_confirmation, send_payment_success, send_order_shipped, send_low_stock_alert

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def order_confirmation(request):
    data = json.loads(request.body)
    send_order_confirmation.delay(
        data['user_email'], data['order_id'],
        data['total_amount'], data.get('items', []),
    )
    return JsonResponse({'queued': True})


@csrf_exempt
@require_POST
def payment_success(request):
    data = json.loads(request.body)
    send_payment_success.delay(
        data.get('user_email', ''), data['order_id'],
        data['payment_id'], data['amount'],
    )
    return JsonResponse({'queued': True})


@csrf_exempt
@require_POST
def order_shipped(request):
    data = json.loads(request.body)
    send_order_shipped.delay(
        data['user_email'], data['order_id'], data.get('tracking_info'),
    )
    return JsonResponse({'queued': True})


@csrf_exempt
@require_POST
def low_stock_alert(request):
    data = json.loads(request.body)
    send_low_stock_alert.delay(
        data['admin_emails'], data['product_name'],
        data['sku'], data['current_stock'], data['service'],
    )
    return JsonResponse({'queued': True})
