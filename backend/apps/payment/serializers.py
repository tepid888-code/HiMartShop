from rest_framework import serializers
from apps.payment.models import Payment, PaymentTransaction, RefundRequest


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'transaction_type', 'amount', 'external_transaction_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display', read_only=True
    )

    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_method', 'payment_method_display',
                  'status', 'status_display', 'transaction_id', 'reference_number',
                  'created_at', 'updated_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']


class PaymentDetailSerializer(PaymentSerializer):
    transactions = PaymentTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_method', 'payment_method_display',
                  'status', 'status_display', 'transaction_id', 'reference_number',
                  'transactions', 'created_at', 'updated_at', 'completed_at']
        read_only_fields = ['id', 'transactions', 'created_at', 'updated_at', 'completed_at']


class MPesaPaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class StripePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    stripe_token = serializers.CharField(max_length=200)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class RefundRequestSerializer(serializers.ModelSerializer):
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = RefundRequest
        fields = ['id', 'order', 'reason', 'reason_display', 'description', 'amount',
                  'status', 'status_display', 'created_at', 'updated_at', 'processed_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'processed_at']

