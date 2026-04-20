from django.db import models


class Cart(models.Model):
    user_id = models.IntegerField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart(user_id={self.user_id})"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    product_service = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255, blank=True)
    product_sku = models.CharField(max_length=100, blank=True)
    product_image = models.URLField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'product_id', 'product_service')

    def __str__(self):
        return f"CartItem(product={self.product_id}, qty={self.quantity}, price={self.price})"

    @property
    def subtotal(self):
        return self.quantity * self.price
