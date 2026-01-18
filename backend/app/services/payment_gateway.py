"""
Payment Gateway Service
Handles Razorpay payment gateway integration
"""

try:
    import razorpay

    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    razorpay = None

from typing import Optional, Dict, Any
from datetime import datetime
from app.core.config import settings


class PaymentGatewayService:
    """Service for handling payment gateway operations"""

    def __init__(self):
        """Initialize Razorpay client"""
        if not RAZORPAY_AVAILABLE:
            self.client = None
            self.enabled = False
            return

        if settings.PAYMENT_ENABLED and settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
            try:
                self.client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                )
                self.enabled = True
            except Exception:
                self.client = None
                self.enabled = False
        else:
            self.client = None
            self.enabled = False

    def is_enabled(self) -> bool:
        """Check if payment gateway is enabled"""
        return self.enabled

    def create_order(
        self,
        amount: float,
        currency: str = "INR",
        receipt: Optional[str] = None,
        notes: Optional[Dict[str, str]] = None,
        customer_id: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_contact: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a Razorpay order

        Args:
            amount: Amount in rupees (will be converted to paise)
            currency: Currency code (default: INR)
            receipt: Receipt number/ID
            notes: Additional notes/metadata
            customer_id: Customer ID
            customer_name: Customer name
            customer_email: Customer email
            customer_contact: Customer phone number

        Returns:
            Order details from Razorpay
        """
        if not self.enabled:
            raise ValueError("Payment gateway is not enabled")

        # Convert amount to paise (smallest currency unit)
        amount_paise = int(amount * 100)

        order_data = {
            "amount": amount_paise,
            "currency": currency,
            "payment_capture": 1,  # Auto-capture payment
        }

        if receipt:
            order_data["receipt"] = receipt

        if notes:
            order_data["notes"] = notes

        # Customer details
        if customer_id or customer_name or customer_email or customer_contact:
            order_data["customer"] = {}
            if customer_id:
                order_data["customer"]["id"] = customer_id
            if customer_name:
                order_data["customer"]["name"] = customer_name
            if customer_email:
                order_data["customer"]["email"] = customer_email
            if customer_contact:
                order_data["customer"]["contact"] = customer_contact

        try:
            order = self.client.order.create(data=order_data)
            return order
        except Exception as e:
            raise Exception(f"Failed to create Razorpay order: {str(e)}")

    def verify_payment(
        self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature

        Args:
            razorpay_order_id: Order ID from Razorpay
            razorpay_payment_id: Payment ID from Razorpay
            razorpay_signature: Signature from Razorpay

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.enabled:
            raise ValueError("Payment gateway is not enabled")

        if not RAZORPAY_AVAILABLE:
            raise ValueError("Razorpay package is not installed")

        try:
            # Create signature string
            signature_string = f"{razorpay_order_id}|{razorpay_payment_id}"

            # Verify signature
            self.client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                }
            )

            return True
        except Exception as e:
            # Check if it's a signature verification error (only if razorpay is available)
            if RAZORPAY_AVAILABLE:
                error_type = type(e).__name__
                if error_type == "SignatureVerificationError":
                    return False
            # Re-raise as generic exception
            raise Exception(f"Error verifying payment: {str(e)}")

    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment details from Razorpay

        Args:
            payment_id: Razorpay payment ID

        Returns:
            Payment details from Razorpay
        """
        if not self.enabled:
            raise ValueError("Payment gateway is not enabled")

        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            raise Exception(f"Failed to fetch payment: {str(e)}")

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get order details from Razorpay

        Args:
            order_id: Razorpay order ID

        Returns:
            Order details from Razorpay
        """
        if not self.enabled:
            raise ValueError("Payment gateway is not enabled")

        try:
            order = self.client.order.fetch(order_id)
            return order
        except Exception as e:
            raise Exception(f"Failed to fetch order: {str(e)}")

    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        notes: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a refund for a payment

        Args:
            payment_id: Razorpay payment ID
            amount: Refund amount (if None, full refund)
            notes: Refund notes

        Returns:
            Refund details from Razorpay
        """
        if not self.enabled:
            raise ValueError("Payment gateway is not enabled")

        refund_data = {}

        if amount:
            # Convert to paise
            refund_data["amount"] = int(amount * 100)

        if notes:
            refund_data["notes"] = notes

        try:
            refund = self.client.payment.refund(payment_id, refund_data)
            return refund
        except Exception as e:
            raise Exception(f"Failed to create refund: {str(e)}")

    def get_refunds(self, payment_id: str) -> list:
        """
        Get all refunds for a payment

        Args:
            payment_id: Razorpay payment ID

        Returns:
            List of refunds
        """
        if not self.enabled:
            raise ValueError("Payment gateway is not enabled")

        try:
            refunds = self.client.payment.fetch(payment_id).get("refunds", [])
            return refunds
        except Exception as e:
            raise Exception(f"Failed to fetch refunds: {str(e)}")

    def create_payment_link(
        self,
        amount: float,
        currency: str = "INR",
        description: str = "",
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_contact: Optional[str] = None,
        notes: Optional[Dict[str, str]] = None,
        expire_by: Optional[int] = None,  # Unix timestamp
    ) -> Dict[str, Any]:
        """
        Create a payment link (for email/SMS sharing)

        Args:
            amount: Amount in rupees
            currency: Currency code (default: INR)
            description: Payment description
            customer_name: Customer name
            customer_email: Customer email
            customer_contact: Customer phone
            notes: Additional notes
            expire_by: Expiry timestamp (Unix)

        Returns:
            Payment link details from Razorpay
        """
        if not self.enabled:
            raise ValueError("Payment gateway is not enabled")

        # Convert amount to paise
        amount_paise = int(amount * 100)

        payment_link_data = {
            "amount": amount_paise,
            "currency": currency,
            "description": description,
        }

        if customer_name or customer_email or customer_contact:
            payment_link_data["customer"] = {}
            if customer_name:
                payment_link_data["customer"]["name"] = customer_name
            if customer_email:
                payment_link_data["customer"]["email"] = customer_email
            if customer_contact:
                payment_link_data["customer"]["contact"] = customer_contact

        if notes:
            payment_link_data["notes"] = notes

        if expire_by:
            payment_link_data["expire_by"] = expire_by

        try:
            payment_link = self.client.payment_link.create(payment_link_data)
            return payment_link
        except Exception as e:
            raise Exception(f"Failed to create payment link: {str(e)}")

    def verify_webhook_signature(
        self, payload: str, signature: str, secret: Optional[str] = None
    ) -> bool:
        """
        Verify Razorpay webhook signature

        Args:
            payload: Webhook payload (string)
            signature: Webhook signature from headers
            secret: Webhook secret (if different from key secret)

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.enabled:
            raise ValueError("Payment gateway is not enabled")

        if not RAZORPAY_AVAILABLE:
            raise ValueError("Razorpay package is not installed")

        try:
            webhook_secret = secret or settings.RAZORPAY_KEY_SECRET
            self.client.utility.verify_webhook_signature(payload, signature, webhook_secret)
            return True
        except Exception as e:
            # Check if it's a signature verification error (only if razorpay is available)
            if RAZORPAY_AVAILABLE:
                error_type = type(e).__name__
                if error_type == "SignatureVerificationError":
                    return False
            # Re-raise as generic exception
            raise Exception(f"Error verifying webhook: {str(e)}")


# Global instance
payment_gateway_service = PaymentGatewayService()
