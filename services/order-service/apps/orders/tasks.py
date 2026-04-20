"""
Celery tasks for order processing.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue='orders')
def send_order_confirmation_email(self, order_id, user_email):
    """Send order confirmation email to customer."""
    try:
        logger.info(f"Sending order confirmation email for order #{order_id} to {user_email}")
        # In production, integrate with email service (SendGrid, SES, etc.)
        # For now, just log
        logger.info(f"Order #{order_id} confirmation email sent to {user_email}")
        return {'status': 'sent', 'order_id': order_id, 'email': user_email}
    except Exception as exc:
        logger.error(f"Failed to send email for order #{order_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, queue='orders')
def update_inventory_after_order(self, order_id, items):
    """Update inventory in product services after order is confirmed."""
    import requests
    try:
        logger.info(f"Updating inventory for order #{order_id}")
        for item in items:
            service = item.get('product_service')
            product_id = item.get('product_id')
            quantity = item.get('quantity')

            # Map service name to port
            service_ports = {
                'laptop': 8010, 'mobile': 8011, 'tablet': 8012,
                'audio': 8013, 'accessory': 8014, 'smartwatch': 8015,
                'camera': 8016, 'monitor': 8017, 'keyboard': 8018,
                'mouse': 8019, 'printer': 8020, 'networking': 8021,
                'storage': 8022, 'component': 8023, 'gaminggear': 8024,
            }
            port = service_ports.get(service)
            if port:
                url = f"http://{service}-service:{port}/products/{product_id}/reserve/"
                try:
                    requests.post(url, json={'quantity': quantity}, timeout=5)
                except requests.RequestException as e:
                    logger.warning(f"Failed to update inventory for {service} product {product_id}: {e}")

        return {'status': 'updated', 'order_id': order_id}
    except Exception as exc:
        logger.error(f"Inventory update failed for order #{order_id}: {exc}")
        raise self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=3, queue='orders')
def process_payment_webhook(self, payment_data):
    """Process incoming payment webhook and update order status."""
    try:
        order_id = payment_data.get('order_id')
        payment_status = payment_data.get('status')
        logger.info(f"Processing payment webhook for order #{order_id}, status={payment_status}")

        from .models import Order, OrderStatusLog
        try:
            order = Order.objects.get(id=order_id)
            if payment_status == 'COMPLETED':
                old_status = order.status
                order.status = 'CONFIRMED'
                order.save()
                OrderStatusLog.objects.create(
                    order=order,
                    old_status=old_status,
                    new_status='CONFIRMED',
                    note='Payment confirmed via webhook.',
                )
        except Order.DoesNotExist:
            logger.error(f"Order #{order_id} not found for payment webhook")

        return {'status': 'processed', 'order_id': order_id}
    except Exception as exc:
        logger.error(f"Payment webhook processing failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
