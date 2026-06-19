from rest_framework import serializers
from apps.promotions.models import Coupon, CouponUsage

class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()
    discount_value_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = ['id', 'code', 'description', 'discount_type', 'discount_value',
                  'discount_value_formatted', 'min_purchase', 'max_discount',
                  'is_valid', 'valid_from', 'valid_to']
        read_only_fields = ['id']

    def get_is_valid(self, obj):
        return obj.is_valid()

    def get_discount_value_formatted(self, obj):
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}%"
        else:
            return f"KES {obj.discount_value}"

class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

class CouponUsageSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)

    class Meta:
        model = CouponUsage
        fields = ['id', 'coupon_code', 'used_at']
        read_only_fields = ['id', 'used_at']
