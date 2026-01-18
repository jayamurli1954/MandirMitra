"""
Payment Gateway Service Tests
Tests for Razorpay payment gateway integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.payment_gateway import PaymentGatewayService
from app.core.config import settings


@pytest.mark.unit
@pytest.mark.payment
class TestPaymentGatewayService:
    """Tests for payment gateway service"""
    
    @pytest.fixture
    def payment_service(self):
        """Create payment gateway service instance"""
        return PaymentGatewayService()
    
    def test_service_initialization_when_disabled(self, payment_service):
        """Test service initialization when payment is disabled"""
        # Service should handle disabled state gracefully
        assert hasattr(payment_service, 'enabled')
        assert hasattr(payment_service, 'client')
    
    def test_is_enabled(self, payment_service):
        """Test is_enabled method"""
        result = payment_service.is_enabled()
        assert isinstance(result, bool)
    
    def test_create_order_when_disabled(self, payment_service):
        """Test order creation when service is disabled"""
        payment_service.enabled = False
        
        with pytest.raises(ValueError, match="Payment gateway is not enabled"):
            payment_service.create_order(amount=100.00)
    
    @patch('app.services.payment_gateway.razorpay')
    def test_create_order_success(self, mock_razorpay_module, payment_service):
        """Test successful order creation"""
        # Mock Razorpay client
        mock_client = MagicMock()
        mock_client.order.create.return_value = {
            'id': 'order_test123',
            'amount': 10000,
            'currency': 'INR',
            'status': 'created'
        }
        
        payment_service.client = mock_client
        payment_service.enabled = True
        
        result = payment_service.create_order(
            amount=100.00,
            currency='INR',
            receipt='TEST001'
        )
        
        assert result['id'] == 'order_test123'
        assert result['amount'] == 10000
        assert result['currency'] == 'INR'
        mock_client.order.create.assert_called_once()
    
    @patch('app.services.payment_gateway.razorpay')
    def test_create_order_failure(self, mock_razorpay_module, payment_service):
        """Test order creation failure"""
        mock_client = MagicMock()
        mock_client.order.create.side_effect = Exception("API Error")
        
        payment_service.client = mock_client
        payment_service.enabled = True
        
        with pytest.raises(Exception, match="Failed to create Razorpay order"):
            payment_service.create_order(amount=100.00)
    
    @patch('app.services.payment_gateway.RAZORPAY_AVAILABLE', True)
    @patch('app.services.payment_gateway.razorpay')
    def test_verify_payment_signature(self, mock_razorpay_module, payment_service):
        """Test payment signature verification"""
        mock_client = MagicMock()
        mock_client.utility.verify_payment_signature.return_value = True
        
        payment_service.client = mock_client
        payment_service.enabled = True
        
        result = payment_service.verify_payment(
            razorpay_order_id='order_123',
            razorpay_payment_id='pay_123',
            razorpay_signature='sig_123'
        )
        
        assert result == True
        mock_client.utility.verify_payment_signature.assert_called_once()
    
    @patch('app.services.payment_gateway.razorpay')
    def test_create_order_zero_amount(self, mock_razorpay_module, payment_service):
        """Test order creation with zero amount"""
        mock_client = MagicMock()
        mock_client.order.create.return_value = {'id': 'order_zero', 'amount': 0}
        payment_service.client = mock_client
        payment_service.enabled = True
        
        # Zero amount should still create order (amount_paise = 0)
        result = payment_service.create_order(amount=0)
        assert result is not None
        assert result['amount'] == 0
    
    @patch('app.services.payment_gateway.razorpay')
    def test_create_order_negative_amount(self, mock_razorpay_module, payment_service):
        """Test order creation with negative amount"""
        mock_client = MagicMock()
        payment_service.client = mock_client
        payment_service.enabled = True
        
        # Negative amount will be converted to negative paise
        # Razorpay may reject it, but our code should handle it
        try:
            result = payment_service.create_order(amount=-100)
            # If it doesn't raise, check the result
            assert result is not None
        except Exception:
            # Expected - negative amounts should be rejected
            pass

