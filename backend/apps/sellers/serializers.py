from rest_framework import serializers
from apps.sellers.models import SellerProfile, SellerStats, SellerWithdrawal, SellerMessage

class SellerProfileSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = SellerProfile
        fields = ['id', 'store', 'store_name', 'user_email', 'verification_status', 'is_active',
                  'total_sales', 'total_products', 'average_rating', 'followers', 'created_at']

class SellerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerStats
        fields = ['id', 'date', 'orders', 'revenue', 'refunds', 'views', 'clicks', 'favorites']

class SellerWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerWithdrawal
        fields = ['id', 'amount', 'status', 'bank_account', 'bank_name', 'requested_at', 'completed_at']

class SellerMessageSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = SellerMessage
        fields = ['id', 'message_type', 'subject', 'message', 'customer_name', 'is_read',
                  'reply', 'created_at', 'replied_at']
