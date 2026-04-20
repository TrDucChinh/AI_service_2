import logging
import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30, queue='payments')
def process_payment(self, payment_id, order_id, amount, user_id):
    """Simulate async payment processing and notify order service on success."""
    try:
        from apps.payments.models import Payment
        payment = Payment.objects.get(id=payment_id)
        payment.status = 'COMPLETED'
        payment.save(update_fields=['status'])

        order_service_url = getattr(settings, 'ORDER_SERVICE_URL', 'http://order-service:8004')
        requests.patch(
            f'{order_service_url}/orders/{order_id}/',
            json={'status': 'CONFIRMED', 'payment_id': payment_id},
            timeout=10,
        )

        notify_payment_success.delay(payment_id, order_id, user_id, float(amount))
        logger.info('Payment %s processed for order %s', payment_id, order_id)
    except Exception as exc:
        logger.error('Payment processing failed for payment %s: %s', payment_id, exc)
        raise self.retry(exc=exc)


@shared_task(queue='payments')
def notify_payment_success(payment_id, order_id, user_id, amount):
    """Send payment success notification via notification service."""
    notification_url = getattr(settings, 'NOTIFICATION_SERVICE_URL', 'http://notification-service:8026')
    try:
        requests.post(
            f'{notification_url}/notifications/payment-success/',
            json={'payment_id': payment_id, 'order_id': order_id, 'user_id': user_id, 'amount': amount},
            timeout=5,
        )
    except Exception as exc:
        logger.warning('Failed to send payment notification: %s', exc)


@shared_task(queue='payments')
def refund_payment(payment_id, reason='Customer request'):
    """Process a payment refund."""
    try:
        from apps.payments.models import Payment
        payment = Payment.objects.get(id=payment_id)
        payment.status = 'REFUNDED'
        payment.save(update_fields=['status'])
        logger.info('Payment %s refunded: %s', payment_id, reason)
    except Exception as exc:
        logger.error('Refund failed for payment %s: %s', payment_id, exc)
        raise
