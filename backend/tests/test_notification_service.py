"""
Notification Service Tests
Tests for SMS and Email notification services
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.notification_service import NotificationService
import requests


@pytest.mark.unit
@pytest.mark.notifications
class TestNotificationService:
    """Tests for notification service"""
    
    @pytest.fixture
    def notification_service(self):
        """Create notification service instance"""
        return NotificationService()
    
    def test_send_sms_when_disabled(self, notification_service):
        """Test SMS sending when service is disabled"""
        notification_service.sms_enabled = False
        
        result = notification_service.send_sms("9876543210", "Test message")
        
        assert result['success'] == False
        assert 'not enabled' in result.get('error', '').lower()
    
    def test_send_sms_invalid_phone(self, notification_service):
        """Test SMS with invalid phone number"""
        notification_service.sms_enabled = True
        
        # Test too short phone
        result = notification_service.send_sms("123", "Test message")
        assert result['success'] == False
        assert 'Invalid phone' in result.get('error', '')
        
        # Test empty phone
        result = notification_service.send_sms("", "Test message")
        assert result['success'] == False
    
    @patch('app.services.notification_service.requests.post')
    def test_send_sms_success(self, mock_post, notification_service):
        """Test successful SMS sending"""
        notification_service.sms_enabled = True
        notification_service.sms_api_key = "test_key"
        notification_service.sms_sender_id = "TEST"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "SMS sent", "message_id": "msg123"}
        mock_post.return_value = mock_response
        
        result = notification_service.send_sms("9876543210", "Test message")
        
        assert result['success'] == True
        assert 'message_id' in result
        mock_post.assert_called_once()
    
    @patch('app.services.notification_service.requests.post')
    def test_send_sms_api_failure(self, mock_post, notification_service):
        """Test SMS sending when API fails"""
        notification_service.sms_enabled = True
        notification_service.sms_api_key = "test_key"
        
        mock_post.side_effect = requests.RequestException("API Error")
        
        result = notification_service.send_sms("9876543210", "Test message")
        
        assert result['success'] == False
        assert 'error' in result
    
    @patch('app.services.notification_service.requests.post')
    def test_send_sms_api_error_response(self, mock_post, notification_service):
        """Test SMS sending when API returns error"""
        notification_service.sms_enabled = True
        notification_service.sms_api_key = "test_key"
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_post.return_value = mock_response
        
        result = notification_service.send_sms("9876543210", "Test message")
        
        assert result['success'] == False
        assert 'error' in result
    
    def test_send_email_when_disabled(self, notification_service):
        """Test email sending when service is disabled"""
        notification_service.email_enabled = False
        
        result = notification_service.send_email(
            to_email="test@example.com",
            subject="Test",
            body="Test message"
        )
        
        assert result['success'] == False
    
    def test_send_email_invalid_address(self, notification_service):
        """Test email with invalid address"""
        notification_service.email_enabled = True
        
        # Test invalid email format
        result = notification_service.send_email(
            to_email="invalid-email",
            subject="Test",
            body="Test message"
        )
        
        assert result['success'] == False
        assert 'Invalid email' in result.get('error', '')
    
    @patch('app.services.notification_service.requests.post')
    def test_send_email_success(self, mock_post, notification_service):
        """Test successful email sending"""
        notification_service.email_enabled = True
        notification_service.email_api_key = "test_key"
        notification_service.email_from = "test@temple.com"
        
        mock_response = Mock()
        mock_response.status_code = 202  # SendGrid returns 202, not 200
        mock_response.headers = {"X-Message-Id": "email123"}
        mock_post.return_value = mock_response
        
        result = notification_service.send_email(
            to_email="test@example.com",
            subject="Test",
            body="Test message"
        )
        
        assert result['success'] == True
        mock_post.assert_called_once()
    
    @patch('app.services.notification_service.requests.post')
    def test_send_email_api_failure(self, mock_post, notification_service):
        """Test email sending when API fails"""
        notification_service.email_enabled = True
        notification_service.email_api_key = "test_key"
        
        mock_post.side_effect = requests.RequestException("API Error")
        
        result = notification_service.send_email(
            to_email="test@example.com",
            subject="Test",
            body="Test message"
        )
        
        assert result['success'] == False
        assert 'error' in result

