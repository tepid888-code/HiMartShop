from django.conf import settings
import requests
from apps.payment.models import Payment, PaymentTransaction


class MPesaService:
    """M-Pesa Payment Service"""

    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.environment = settings.MPESA_ENVIRONMENT
        self.base_url = (
            "https://sandbox.safaricom.co.ke"
            if self.environment == "sandbox"
            else "https://api.safaricom.co.ke"
        )

    def get_access_token(self):
        """Get M-Pesa Access Token"""
        auth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(
            auth_url,
            auth=(self.consumer_key, self.consumer_secret),
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        raise Exception(f"Failed to get M-Pesa access token: {response.text}")

    def initiate_payment(self, phone, amount, order_id):
        """Initiate M-Pesa STK Push"""
        try:
            access_token = self.get_access_token()

            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"

            import time
            timestamp = str(int(time.time() * 1000))

            # Generate password
            import base64
            from datetime import datetime
            timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
            password = base64.b64encode(
                f"{self.shortcode}{self.passkey}{timestamp_str}".encode()
            ).decode()

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp_str,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone,
                "PartyB": self.shortcode,
                "PhoneNumber": phone,
                "CallBackURL": f"{settings.DOMAIN_URL}/api/payments/mpesa/callback/",
                "AccountReference": f"Order-{order_id}",
                "TransactionDesc": f"Payment for Order {order_id}",
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "checkout_request_id": data.get("CheckoutRequestID"),
                    "message": data.get("ResponseDescription"),
                }
            else:
                return {
                    "status": "error",
                    "message": response.json().get("errorMessage", "STK Push failed"),
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def verify_transaction(self, transaction_id):
        """Verify M-Pesa transaction status"""
        # This would typically be called after receiving a callback
        pass

    def process_callback(self, callback_data, payment):
        """Process M-Pesa callback"""
        result_code = callback_data.get("Body", {}).get("stkCallback", {}).get("ResultCode")

        if result_code == 0:
            # Payment successful
            payment_data = (
                callback_data.get("Body", {})
                .get("stkCallback", {})
                .get("CallbackMetadata", {})
                .get("Item", [])
            )

            transaction_id = None
            for item in payment_data:
                if item.get("Name") == "MpesaReceiptNumber":
                    transaction_id = item.get("Value")
                    break

            payment.status = "success"
            payment.transaction_id = transaction_id
            payment.save()

            # Update order payment status
            payment.order.payment_status = "paid"
            payment.order.status = "confirmed"
            payment.order.save()

            return True
        else:
            payment.status = "failed"
            payment.save()
            return False


class StripeService:
    """Stripe Payment Service"""

    def __init__(self):
        self.secret_key = settings.STRIPE_SECRET_KEY
        self.public_key = settings.STRIPE_PUBLIC_KEY
        import stripe
        stripe.api_key = self.secret_key
        self.stripe = stripe

    def create_payment_intent(self, amount, order_id, customer_email=None):
        """Create Stripe Payment Intent"""
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency="kes",
                description=f"Order {order_id}",
                metadata={"order_id": order_id},
            )
            return {
                "status": "success",
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def confirm_payment(self, payment_intent_id):
        """Confirm payment intent"""
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == "succeeded":
                return {"status": "success", "message": "Payment succeeded"}
            elif intent.status == "processing":
                return {"status": "processing", "message": "Payment is processing"}
            else:
                return {"status": "error", "message": f"Payment status: {intent.status}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def process_webhook(self, event):
        """Process Stripe webhook event"""
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            order_id = payment_intent.get("metadata", {}).get("order_id")

            try:
                payment = Payment.objects.get(order_id=order_id)
                payment.status = "success"
                payment.transaction_id = payment_intent.id
                payment.save()

                payment.order.payment_status = "paid"
                payment.order.status = "confirmed"
                payment.order.save()

                return True
            except Payment.DoesNotExist:
                return False

        return False

    def create_refund(self, charge_id, amount=None):
        """Create refund"""
        try:
            refund_params = {"charge": charge_id}
            if amount:
                refund_params["amount"] = int(amount * 100)

            refund = self.stripe.Refund.create(**refund_params)
            return {
                "status": "success",
                "refund_id": refund.id,
                "message": "Refund created successfully",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
