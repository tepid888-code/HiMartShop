from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from apps.payment.models import Payment, RefundRequest
from apps.orders.models import Order
from apps.payment.serializers import (
    PaymentSerializer, PaymentDetailSerializer, RefundRequestSerializer,
    MPesaPaymentSerializer, StripePaymentSerializer
)
from apps.payment.services import MPesaService, StripeService


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)\
            .select_related('order', 'user')\
            .prefetch_related('transactions')\
            .order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PaymentDetailSerializer
        elif self.action == 'mpesa_payment':
            return MPesaPaymentSerializer
        elif self.action == 'stripe_payment':
            return StripePaymentSerializer
        elif self.action == 'refund':
            return RefundRequestSerializer
        return PaymentSerializer

    @action(detail=False, methods=['post'])
    def mpesa_payment(self, request):
        """Initiate M-Pesa payment"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data.get('order_id')
        phone = serializer.validated_data.get('phone_number')
        amount = serializer.validated_data.get('amount')

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.payment_status == 'paid':
            return Response(
                {'error': 'Order already paid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create payment record
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=amount,
            payment_method='mpesa',
            status='processing'
        )

        # Initiate M-Pesa payment
        mpesa_service = MPesaService()
        result = mpesa_service.initiate_payment(phone, amount, order_id)

        if result['status'] == 'success':
            payment.reference_number = result.get('checkout_request_id')
            payment.save()
            return Response({
                'payment_id': payment.id,
                'status': 'processing',
                'message': result.get('message'),
                'checkout_request_id': result.get('checkout_request_id'),
            })
        else:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'error': result.get('message')},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def stripe_payment(self, request):
        """Initiate Stripe payment"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data.get('order_id')
        amount = serializer.validated_data.get('amount')

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.payment_status == 'paid':
            return Response(
                {'error': 'Order already paid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create payment record
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=amount,
            payment_method='stripe',
            status='processing'
        )

        # Create Stripe payment intent
        stripe_service = StripeService()
        result = stripe_service.create_payment_intent(amount, order_id, request.user.email)

        if result['status'] == 'success':
            payment.reference_number = result.get('payment_intent_id')
            payment.save()
            return Response({
                'payment_id': payment.id,
                'status': 'processing',
                'client_secret': result.get('client_secret'),
                'payment_intent_id': result.get('payment_intent_id'),
            })
        else:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'error': result.get('message')},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def stripe_confirm(self, request):
        """Confirm Stripe payment"""
        payment_intent_id = request.data.get('payment_intent_id')

        try:
            stripe_service = StripeService()
            result = stripe_service.confirm_payment(payment_intent_id)

            if result['status'] == 'success':
                try:
                    payment = Payment.objects.get(reference_number=payment_intent_id)
                    payment.status = 'success'
                    payment.save()

                    payment.order.payment_status = 'paid'
                    payment.order.status = 'confirmed'
                    payment.order.save()
                except Payment.DoesNotExist:
                    pass

                return Response({'status': 'success', 'message': result.get('message')})
            else:
                return Response(
                    {'status': result['status'], 'message': result.get('message')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Request refund"""
        payment = self.get_object()

        reason = request.data.get('reason')
        description = request.data.get('description', '')
        amount = request.data.get('amount', payment.amount)

        if not reason:
            return Response(
                {'error': 'Reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refund_request = RefundRequest.objects.create(
            order=payment.order,
            user=request.user,
            reason=reason,
            description=description,
            amount=amount,
            status='pending'
        )

        return Response(
            RefundRequestSerializer(refund_request).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def check_status(self, request, pk=None):
        """Check payment status"""
        payment = self.get_object()

        if payment.payment_method == 'stripe':
            stripe_service = StripeService()
            result = stripe_service.confirm_payment(payment.reference_number)

            if result['status'] == 'success' and payment.status != 'success':
                payment.status = 'success'
                payment.save()
                payment.order.payment_status = 'paid'
                payment.order.status = 'confirmed'
                payment.order.save()

        return Response({
            'payment_id': payment.id,
            'status': payment.status,
            'amount': payment.amount,
            'payment_method': payment.payment_method,
        })


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def mpesa_callback(request):
    """M-Pesa callback endpoint"""
    try:
        data = json.loads(request.body)
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        checkout_request_id = (
            data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        )

        payment = Payment.objects.get(reference_number=checkout_request_id)

        mpesa_service = MPesaService()
        mpesa_service.process_callback(data, payment)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """Stripe webhook endpoint"""
    try:
        import stripe
        from django.conf import settings

        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )

        stripe_service = StripeService()
        stripe_service.process_webhook(event)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

