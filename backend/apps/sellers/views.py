from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.sellers.models import SellerProfile, SellerStats, SellerWithdrawal, SellerMessage
from apps.sellers.serializers import (
    SellerProfileSerializer, SellerStatsSerializer,
    SellerWithdrawalSerializer, SellerMessageSerializer
)

class SellerProfileViewSet(viewsets.ModelViewSet):
    """卖家个人资料"""
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SellerProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """获取我的卖家资料"""
        profile = get_object_or_404(SellerProfile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """卖家仪表板"""
        profile = get_object_or_404(SellerProfile, user=request.user)
        stats = SellerStats.objects.filter(seller=profile).order_by('-date')[:7]

        return Response({
            'profile': SellerProfileSerializer(profile).data,
            'recent_stats': SellerStatsSerializer(stats, many=True).data,
            'total_revenue': profile.total_sales,
            'average_rating': profile.average_rating,
            'followers': profile.followers,
        })

class SellerWithdrawalViewSet(viewsets.ModelViewSet):
    """卖家提现管理"""
    serializer_class = SellerWithdrawalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = get_object_or_404(SellerProfile, user=self.request.user)
        return SellerWithdrawal.objects.filter(seller=profile)

    @action(detail=False, methods=['post'])
    def request_withdrawal(self, request):
        """申请提现"""
        profile = get_object_or_404(SellerProfile, user=request.user)
        amount = request.data.get('amount')
        bank_account = request.data.get('bank_account')
        bank_name = request.data.get('bank_name')

        if not amount or not bank_account or not bank_name:
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if float(amount) > profile.total_sales:
            return Response(
                {'error': 'Insufficient balance'},
                status=status.HTTP_400_BAD_REQUEST
            )

        withdrawal = SellerWithdrawal.objects.create(
            seller=profile,
            amount=amount,
            bank_account=bank_account,
            bank_name=bank_name
        )

        return Response(
            SellerWithdrawalSerializer(withdrawal).data,
            status=status.HTTP_201_CREATED
        )

class SellerMessageViewSet(viewsets.ModelViewSet):
    """商家消息"""
    serializer_class = SellerMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = get_object_or_404(SellerProfile, user=self.request.user)
        return SellerMessage.objects.filter(seller=profile)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """回复消息"""
        message = self.get_object()
        reply_text = request.data.get('reply')

        if not reply_text:
            return Response(
                {'error': 'Reply text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        message.reply = reply_text
        message.is_read = True
        message.save()

        return Response(
            SellerMessageSerializer(message).data,
            status=status.HTTP_200_OK
        )
