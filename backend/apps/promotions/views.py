from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.promotions.models import Coupon, CouponUsage
from apps.promotions.serializers import (
    CouponSerializer, CouponApplySerializer, CouponUsageSerializer
)

class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """优惠券视图集"""
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """只返回有效的优惠券"""
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=['post'])
    def validate(self, request):
        """验证优惠券"""
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get('code')
        amount = serializer.validated_data.get('amount')

        coupon = get_object_or_404(Coupon, code=code)

        if not coupon.is_valid():
            return Response(
                {'error': 'Coupon is not valid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if amount < coupon.min_purchase:
            return Response(
                {'error': f'Minimum purchase required: KES {coupon.min_purchase}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        discount = coupon.calculate_discount(amount)

        return Response({
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': str(coupon.discount_value),
            'discount_amount': str(discount),
            'final_amount': str(amount - discount),
        })

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def apply(self, request):
        """应用优惠券"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get('code')
        amount = serializer.validated_data.get('amount')

        coupon = get_object_or_404(Coupon, code=code)

        if not coupon.is_valid():
            return Response(
                {'error': 'Coupon is not valid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查用户使用次数
        usage_count = CouponUsage.objects.filter(
            coupon=coupon,
            user_id=request.user.id
        ).count()

        if usage_count >= coupon.max_uses_per_user:
            return Response(
                {'error': f'You have already used this coupon {usage_count} times'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if amount < coupon.min_purchase:
            return Response(
                {'error': f'Minimum purchase required: KES {coupon.min_purchase}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        discount = coupon.calculate_discount(amount)

        # 记录使用
        CouponUsage.objects.get_or_create(
            coupon=coupon,
            user_id=request.user.id
        )

        # 更新使用次数
        coupon.current_uses += 1
        coupon.save()

        return Response({
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': str(coupon.discount_value),
            'discount_amount': str(discount),
            'final_amount': str(amount - discount),
        })
