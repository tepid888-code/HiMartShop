from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.serializers import NotificationSerializer, NotificationPreferenceSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """通知视图"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读通知数量"""
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': unread_count})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """标记为已读"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """标记所有为已读"""
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return Response({'status': 'success'})

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近的通知（前10条）"""
        notifications = self.get_queryset()[:10]
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

class NotificationPreferenceViewSet(viewsets.ViewSet):
    """通知偏好视图"""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """获取通知偏好"""
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(preference)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """更新通知偏好"""
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(preference, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def get_or_create(self, request):
        """获取或创建通知偏好"""
        preference, created = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(preference)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
