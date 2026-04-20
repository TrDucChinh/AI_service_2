from django.db import models


class Profile(models.Model):
    user_id = models.IntegerField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"Profile(user_id={self.user_id}, name={self.first_name} {self.last_name})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Address(models.Model):
    user_id = models.IntegerField(db_index=True)
    label = models.CharField(max_length=50, default='Home')  # Home, Work, Other
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_addresses'

    def __str__(self):
        return f"{self.label}: {self.street}, {self.city}, {self.country}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Remove default from all other addresses of same user
            Address.objects.filter(user_id=self.user_id, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    user_id = models.IntegerField(db_index=True)
    product_id = models.IntegerField()
    product_service = models.CharField(max_length=50)  # e.g., 'laptop', 'mobile'
    product_name = models.CharField(max_length=255, blank=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_image = models.URLField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_wishlist'
        unique_together = ('user_id', 'product_id', 'product_service')

    def __str__(self):
        return f"Wishlist(user={self.user_id}, product={self.product_id}, service={self.product_service})"
