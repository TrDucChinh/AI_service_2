from rest_framework import serializers
from .models import Profile, Address, Wishlist


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'user_id', 'first_name', 'last_name', 'full_name',
                  'phone', 'avatar', 'bio', 'date_of_birth', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user_id', 'created_at', 'updated_at')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'user_id', 'label', 'street', 'city', 'state',
                  'country', 'zip_code', 'is_default', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user_id', 'created_at', 'updated_at')


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ('id', 'user_id', 'product_id', 'product_service',
                  'product_name', 'product_price', 'product_image', 'added_at')
        read_only_fields = ('id', 'user_id', 'added_at')
