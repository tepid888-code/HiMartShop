import pytest
from rest_framework import status
from unittest.mock import patch, MagicMock
from apps.payment.models import Payment, PaymentMethod, PaymentTransaction, RefundRequest
from apps.orders.models import Order


@pytest.mark.django_db
class TestPaymentViewSet:
    """支付 ViewSet 测试"""

    def test_list_payments(self, authenticated_client, authenticated_user):
        """测试支付列表"""
        response = authenticated_client.get('/api/payments/')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_payment(self, authenticated_client, authenticated_user, sample_product):
        """测试获取单个支付"""
        # 创建订单和支付
        order = Order.objects.create(
            user=authenticated_user,
            status='pending',
            order_number='TEST001'
        )

        payment = Payment.objects.create(
            order=order,
            user=authenticated_user,
            amount=100.00,
            payment_method='cod',
            status='pending'
        )

        response = authenticated_client.get(f'/api/payments/{payment.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == payment.id

    @patch('apps.payment.services.MPesaService.initiate_payment')
    def test_mpesa_payment_initiation(self, mock_mpesa, authenticated_client, authenticated_user, sample_product):
        """测试 M-Pesa 支付初始化"""
        # 创建订单
        order = Order.objects.create(
            user=authenticated_user,
            status='pending',
            order_number='TEST002'
        )

        mock_mpesa.return_value = {
            'status': 'success',
            'checkout_request_id': 'ws_CO_DMZ_12321',
            'message': 'Success'
        }

        payment_data = {
            'order_id': order.id,
            'phone_number': '+254712345678',
            'amount': 100.00
        }

        response = authenticated_client.post(
            '/api/payments/mpesa_payment/',
            payment_data,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'processing'
        assert 'checkout_request_id' in response.data

    @patch('apps.payment.services.StripeService.create_payment_intent')
    def test_stripe_payment_initiation(self, mock_stripe, authenticated_client, authenticated_user):
        """测试 Stripe 支付初始化"""
        # 创建订单
        order = Order.objects.create(
            user=authenticated_user,
            status='pending',
            order_number='TEST003'
        )

        mock_stripe.return_value = {
            'status': 'success',
            'payment_intent_id': 'pi_1234567890',
            'client_secret': 'pi_1234567890_secret_abcdefgh'
        }

        payment_data = {
            'order_id': order.id,
            'amount': 100.00
        }

        response = authenticated_client.post(
            '/api/payments/stripe_payment/',
            payment_data,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'processing'
        assert 'client_secret' in response.data

    @patch('apps.payment.services.StripeService.confirm_payment')
    def test_stripe_payment_confirmation(self, mock_confirm, authenticated_client, authenticated_user):
        """测试 Stripe 支付确认"""
        # 创建订单和支付
        order = Order.objects.create(
            user=authenticated_user,
            status='pending',
            payment_status='pending',
            order_number='TEST004'
        )

        payment = Payment.objects.create(
            order=order,
            user=authenticated_user,
            amount=100.00,
            payment_method='stripe',
            status='processing',
            reference_number='pi_1234567890'
        )

        mock_confirm.return_value = {
            'status': 'success',
            'message': 'Payment succeeded'
        }

        confirm_data = {
            'payment_intent_id': 'pi_1234567890'
        }

        response = authenticated_client.post(
            '/api/payments/stripe_confirm/',
            confirm_data,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK

    def test_mpesa_payment_already_paid(self, authenticated_client, authenticated_user):
        """测试已支付订单不能再支付"""
        order = Order.objects.create(
            user=authenticated_user,
            status='confirmed',
            payment_status='paid',
            order_number='TEST005'
        )

        payment_data = {
            'order_id': order.id,
            'phone_number': '+254712345678',
            'amount': 100.00
        }

        response = authenticated_client.post(
            '/api/payments/mpesa_payment/',
            payment_data,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already paid' in response.data.get('error', '').lower()

    def test_stripe_payment_already_paid(self, authenticated_client, authenticated_user):
        """测试已支付订单不能再 Stripe 支付"""
        order = Order.objects.create(
            user=authenticated_user,
            status='confirmed',
            payment_status='paid',
            order_number='TEST006'
        )

        payment_data = {
            'order_id': order.id,
            'amount': 100.00
        }

        response = authenticated_client.post(
            '/api/payments/stripe_payment/',
            payment_data,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_mpesa_payment_nonexistent_order(self, authenticated_client):
        """测试不存在的订单支付"""
        payment_data = {
            'order_id': 99999,
            'phone_number': '+254712345678',
            'amount': 100.00
        }

        response = authenticated_client.post(
            '/api/payments/mpesa_payment/',
            payment_data,
            format='json'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_stripe_payment_nonexistent_order(self, authenticated_client):
        """测试不存在的订单 Stripe 支付"""
        payment_data = {
            'order_id': 99999,
            'amount': 100.00
        }

        response = authenticated_client.post(
            '/api/payments/stripe_payment/',
            payment_data,
            format='json'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('apps.payment.services.StripeService.confirm_payment')
    def test_check_payment_status_stripe(self, mock_confirm, authenticated_client, authenticated_user):
        """测试检查 Stripe 支付状态"""
        order = Order.objects.create(
            user=authenticated_user,
            status='pending',
            payment_status='pending',
            order_number='TEST007'
        )

        payment = Payment.objects.create(
            order=order,
            user=authenticated_user,
            amount=100.00,
            payment_method='stripe',
            status='processing',
            reference_number='pi_1234567890'
        )

        mock_confirm.return_value = {
            'status': 'success',
            'message': 'Payment succeeded'
        }

        response = authenticated_client.post(
            f'/api/payments/{payment.id}/check_status/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'status' in response.data

    def test_check_payment_status_cod(self, authenticated_client, authenticated_user):
        """测试检查 COD 支付状态"""
        order = Order.objects.create(
            user=authenticated_user,
            status='pending',
            payment_status='pending',
            order_number='TEST008'
        )

        payment = Payment.objects.create(
            order=order,
            user=authenticated_user,
            amount=100.00,
            payment_method='cod',
            status='pending'
        )

        response = authenticated_client.post(
            f'/api/payments/{payment.id}/check_status/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['payment_method'] == 'cod'

    def test_request_refund(self, authenticated_client, authenticated_user):
        """测试请求退款"""
        order = Order.objects.create(
            user=authenticated_user,
            status='confirmed',
            order_number='TEST009'
        )

        payment = Payment.objects.create(
            order=order,
            user=authenticated_user,
            amount=100.00,
            payment_method='mpesa',
            status='success'
        )

        refund_data = {
            'reason': 'quality',
            'description': 'Product has defects',
            'amount': 100.00
        }

        response = authenticated_client.post(
            f'/api/payments/{payment.id}/refund/',
            refund_data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'pending'

    def test_refund_without_reason(self, authenticated_client, authenticated_user):
        """测试不提供理由的退款请求"""
        order = Order.objects.create(
            user=authenticated_user,
            status='confirmed',
            order_number='TEST010'
        )

        payment = Payment.objects.create(
            order=order,
            user=authenticated_user,
            amount=100.00,
            payment_method='mpesa',
            status='success'
        )

        refund_data = {
            'description': 'Product has defects'
        }

        response = authenticated_client.post(
            f'/api/payments/{payment.id}/refund/',
            refund_data,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_payment_filtering_by_status(self, authenticated_client, authenticated_user):
        """测试按状态过滤支付"""
        order = Order.objects.create(
            user=authenticated_user,
            status='pending',
            order_number='TEST011'
        )

        Payment.objects.create(
            order=order,
            user=authenticated_user,
            amount=100.00,
            payment_method='cod',
            status='pending'
        )

        response = authenticated_client.get('/api/payments/?status=pending')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPaymentModel:
    """支付模型测试"""

    def test_create_payment(self, authenticated_user, sample_product):
        """测试创建支付"""
        order = Order.objects.create(
            user=authenticated_user,
            status='pending',
            order_number='TEST012'
        )

        payment = Payment.objects.create(
            order=order,
            user=authenticated_user,
            amount=150.50,
            payment_method='stripe',
            status='processing'
        )

        assert payment.id is not None
        assert payment.amount == 150.50
        assert payment.status == 'processing'

    def test_payment_transaction_creation(self, authenticated_user):
        """测试支付交易创建"""
        order = Order.objects.create(
            user=authenticated_user,
            status='pending',
            order_number='TEST013'
        )

        payment = Payment.objects.create(
            order=order,
            user=authenticated_user,
            amount=100.00,
            payment_method='stripe',
            status='success'
        )

        transaction = PaymentTransaction.objects.create(
            payment=payment,
            transaction_type='payment',
            amount=100.00,
            external_transaction_id='ext_123456'
        )

        assert transaction.payment == payment
        assert transaction.amount == 100.00

    def test_refund_request_creation(self, authenticated_user):
        """测试创建退款请求"""
        order = Order.objects.create(
            user=authenticated_user,
            status='confirmed',
            order_number='TEST014'
        )

        refund = RefundRequest.objects.create(
            order=order,
            user=authenticated_user,
            reason='quality',
            description='Poor quality',
            amount=50.00,
            status='pending'
        )

        assert refund.order == order
        assert refund.status == 'pending'
        assert refund.amount == 50.00

    def test_payment_method_creation(self, authenticated_user):
        """测试支付方式创建"""
        payment_method = PaymentMethod.objects.create(
            method='mpesa',
            user=authenticated_user,
            is_default=True,
            is_active=True
        )

        assert payment_method.user == authenticated_user
        assert payment_method.is_default is True


@pytest.mark.django_db
class TestPaymentIntegration:
    """支付集成测试"""

    @patch('apps.payment.services.MPesaService.initiate_payment')
    def test_mpesa_payment_full_flow(self, mock_mpesa, authenticated_client, authenticated_user):
        """测试 M-Pesa 支付完整流程"""
        # 创建订单
        order = Order.objects.create(
            user=authenticated_user,
            status='pending',
            payment_status='pending',
            order_number='TEST015'
        )

        mock_mpesa.return_value = {
            'status': 'success',
            'checkout_request_id': 'ws_CO_DMZ_test',
            'message': 'Success'
        }

        # 发起支付
        payment_data = {
            'order_id': order.id,
            'phone_number': '+254712345678',
            'amount': 100.00
        }

        response = authenticated_client.post(
            '/api/payments/mpesa_payment/',
            payment_data,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'processing'

        # 验证支付记录创建
        payment = Payment.objects.get(order=order)
        assert payment.payment_method == 'mpesa'
        assert payment.status == 'processing'

    def test_payment_order_isolation(self, authenticated_client, authenticated_user):
        """测试用户只能查看自己的支付"""
        # 创建另一个用户和订单
        from apps.users.models import User
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        order = Order.objects.create(
            user=other_user,
            status='pending',
            order_number='TEST016'
        )

        payment = Payment.objects.create(
            order=order,
            user=other_user,
            amount=100.00,
            payment_method='cod',
            status='pending'
        )

        # 当前用户尝试访问
        response = authenticated_client.get(f'/api/payments/{payment.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_payment_list_belongs_to_current_user(self, authenticated_client, authenticated_user):
        """测试支付列表只显示当前用户的支付"""
        from apps.users.models import User

        other_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='testpass123'
        )

        # 创建当前用户的订单
        order1 = Order.objects.create(
            user=authenticated_user,
            status='pending',
            order_number='TEST017'
        )
        Payment.objects.create(
            order=order1,
            user=authenticated_user,
            amount=100.00,
            payment_method='cod'
        )

        # 创建其他用户的订单
        order2 = Order.objects.create(
            user=other_user,
            status='pending',
            order_number='TEST018'
        )
        Payment.objects.create(
            order=order2,
            user=other_user,
            amount=200.00,
            payment_method='cod'
        )

        response = authenticated_client.get('/api/payments/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
