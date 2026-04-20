import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(queue='notifications')
def send_order_confirmation(user_email, order_id, total_amount, items):
    subject = f'Order Confirmation #{order_id}'
    body = (
        f'Thank you for your order!\n\n'
        f'Order ID: #{order_id}\n'
        f'Total: ${total_amount:.2f}\n\n'
        f'Items:\n' +
        '\n'.join(f"  - {item['name']} x{item['quantity']} @ ${item['price']}" for item in items) +
        '\n\nWe will notify you when your order ships.'
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
        logger.info('Order confirmation sent to %s for order #%s', user_email, order_id)
    except Exception as exc:
        logger.error('Failed to send order confirmation: %s', exc)


@shared_task(queue='notifications')
def send_payment_success(user_email, order_id, payment_id, amount):
    subject = f'Payment Confirmed for Order #{order_id}'
    body = (
        f'Your payment has been successfully processed.\n\n'
        f'Payment ID: {payment_id}\n'
        f'Order ID: #{order_id}\n'
        f'Amount: ${amount:.2f}\n\n'
        f'Your order is now being processed.'
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
    except Exception as exc:
        logger.error('Failed to send payment confirmation: %s', exc)


@shared_task(queue='notifications')
def send_order_shipped(user_email, order_id, tracking_info=None):
    subject = f'Your Order #{order_id} Has Shipped!'
    body = f'Great news! Your order #{order_id} is on its way.\n'
    if tracking_info:
        body += f'\nTracking info: {tracking_info}'
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
    except Exception as exc:
        logger.error('Failed to send shipment notification: %s', exc)


@shared_task(queue='notifications')
def send_low_stock_alert(admin_emails, product_name, sku, current_stock, service):
    subject = f'[Low Stock] {product_name} ({sku})'
    body = (
        f'Low stock alert!\n\n'
        f'Product: {product_name}\n'
        f'SKU: {sku}\n'
        f'Service: {service}\n'
        f'Current stock: {current_stock} units\n\n'
        f'Please restock soon.'
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, admin_emails, fail_silently=False)
    except Exception as exc:
        logger.error('Failed to send low stock alert: %s', exc)
