"""
Notification Service
Handles SMS and Email notifications for donations and sevas
"""

import requests
from typing import Optional, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending SMS and Email notifications"""

    def __init__(self):
        self.sms_enabled = getattr(settings, "SMS_ENABLED", False)
        self.email_enabled = getattr(settings, "EMAIL_ENABLED", False)
        self.sms_provider = getattr(settings, "SMS_PROVIDER", "MSG91")
        self.sms_api_key = getattr(settings, "SMS_API_KEY", None)
        self.sms_sender_id = getattr(settings, "SMS_SENDER_ID", None)
        self.sms_template_id = getattr(settings, "SMS_TEMPLATE_ID", None)
        self.infobip_base_url = getattr(settings, "INFOBIP_BASE_URL", "https://api.infobip.com")
        self.sms_test_mode = getattr(settings, "SMS_TEST_MODE", False)
        self.sms_test_recipient = getattr(settings, "SMS_TEST_RECIPIENT", None)
        self.email_api_key = getattr(settings, "EMAIL_API_KEY", None)
        self.email_from = getattr(settings, "EMAIL_FROM", None)

    @staticmethod
    def _digits_only(value: str) -> str:
        return "".join(ch for ch in str(value or "") if ch.isdigit())

    def _normalize_phone_for_msg91(self, phone: str) -> str:
        normalized_phone = self._digits_only(phone)
        if len(normalized_phone) == 10:
            normalized_phone = f"91{normalized_phone}"
        return normalized_phone

    def _normalize_phone_for_infobip(self, phone: str) -> str:
        normalized_phone = self._digits_only(phone)
        if len(normalized_phone) == 10:
            normalized_phone = f"91{normalized_phone}"
        if not normalized_phone.startswith("+"):
            normalized_phone = f"+{normalized_phone}"
        return normalized_phone

    def send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Send SMS notification
        Returns: {"success": bool, "message_id": str, "error": str}
        """
        if not self.sms_enabled:
            logger.info(f"SMS disabled, would send to {phone}: {message[:50]}...")
            return {"success": False, "error": "SMS service not enabled"}

        routed_to_test_number = False
        if self.sms_test_mode:
            if not self.sms_test_recipient:
                logger.warning("SMS test mode is enabled but SMS_TEST_RECIPIENT is not configured")
                return {"success": False, "error": "SMS test recipient not configured"}
            logger.info(
                f"SMS test mode active: rerouting SMS from {phone} to {self.sms_test_recipient}"
            )
            phone = self.sms_test_recipient
            routed_to_test_number = True

        if not phone or len(phone) < 10:
            return {"success": False, "error": "Invalid phone number"}

        try:
            provider = (self.sms_provider or "MSG91").strip().upper()
            if provider == "MSG91":
                if not self.sms_api_key:
                    logger.warning("SMS API key not configured")
                    return {"success": False, "error": "SMS API key not configured"}
                if not self.sms_template_id:
                    logger.warning("SMS template ID not configured")
                    return {"success": False, "error": "SMS template ID not configured"}

                normalized_phone = self._normalize_phone_for_msg91(phone)
                url = "https://control.msg91.com/api/v5/flow/"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "authkey": self.sms_api_key,
                }
                payload = {
                    "template_id": self.sms_template_id,
                    "sender": self.sms_sender_id or "MANDIR",
                    "short_url": "0",
                    "mobiles": normalized_phone,
                    "VAR1": message,  # Template variable
                }

                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "message_id": result.get("request_id", ""),
                        "provider": "MSG91",
                        "test_mode_routed": routed_to_test_number,
                    }

                logger.error(f"SMS API error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"API error: {response.status_code}"}

            if provider == "INFOBIP":
                if not self.sms_api_key:
                    logger.warning("SMS API key not configured")
                    return {"success": False, "error": "SMS API key not configured"}
                if not self.sms_sender_id:
                    logger.warning("SMS sender ID not configured")
                    return {"success": False, "error": "SMS sender ID not configured"}

                normalized_phone = self._normalize_phone_for_infobip(phone)
                base_url = (self.infobip_base_url or "https://api.infobip.com").rstrip("/")
                url = f"{base_url}/sms/2/text/advanced"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"App {self.sms_api_key}",
                }
                payload = {
                    "messages": [
                        {
                            "from": self.sms_sender_id,
                            "destinations": [{"to": normalized_phone}],
                            "text": message,
                        }
                    ]
                }

                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if 200 <= response.status_code < 300:
                    result = response.json()
                    message_id = ""
                    if isinstance(result, dict):
                        messages = result.get("messages") or []
                        if messages and isinstance(messages[0], dict):
                            message_id = messages[0].get("messageId", "")
                    return {
                        "success": True,
                        "message_id": message_id,
                        "provider": "INFOBIP",
                        "test_mode_routed": routed_to_test_number,
                    }

                logger.error(f"Infobip SMS API error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"API error: {response.status_code}"}

            logger.warning(f"SMS provider '{provider}' is not implemented")
            return {"success": False, "error": f"SMS provider '{provider}' not supported"}

        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_email(
        self, to_email: str, subject: str, body: str, html_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send Email notification
        Returns: {"success": bool, "message_id": str, "error": str}
        """
        if not self.email_enabled:
            logger.info(f"Email disabled, would send to {to_email}: {subject}")
            return {"success": False, "error": "Email service not enabled"}

        if not to_email or "@" not in to_email:
            return {"success": False, "error": "Invalid email address"}

        try:
            # SendGrid API integration
            # You can replace with AWS SES, Mailgun, etc.
            if self.email_api_key:
                url = "https://api.sendgrid.com/v3/mail/send"
                headers = {
                    "Authorization": f"Bearer {self.email_api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
                    "from": {"email": self.email_from or "noreply@MandirMitra.com"},
                    "content": [{"type": "text/plain", "value": body}],
                }

                if html_body:
                    payload["content"].append({"type": "text/html", "value": html_body})

                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code == 202:
                    return {
                        "success": True,
                        "message_id": response.headers.get("X-Message-Id", ""),
                        "provider": "SendGrid",
                    }
                else:
                    logger.error(f"Email API error: {response.status_code} - {response.text}")
                    return {"success": False, "error": f"API error: {response.status_code}"}
            else:
                logger.warning("Email API key not configured")
                return {"success": False, "error": "Email API key not configured"}

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_donation_receipt(self, donation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send donation receipt via SMS and Email
        donation_data: {
            "devotee_name": str,
            "phone": str,
            "email": str,
            "receipt_number": str,
            "amount": float,
            "date": str,
            "category": str,
            "pdf_url": Optional[str]
        }
        """
        results = {"sms": None, "email": None}

        # SMS
        if donation_data.get("phone"):
            sms_message = (
                f"Dear {donation_data.get('devotee_name', 'Devotee')}, "
                f"Thank you for your donation of ₹{donation_data.get('amount', 0):,.2f} "
                f"on {donation_data.get('date', '')}. "
                f"Receipt No: {donation_data.get('receipt_number', '')}. "
                f"MandirMitra"
            )
            results["sms"] = self.send_sms(donation_data["phone"], sms_message)

        # Email
        if donation_data.get("email"):
            subject = f"Donation Receipt - {donation_data.get('receipt_number', '')}"
            body = f"""
Dear {donation_data.get('devotee_name', 'Devotee')},

Thank you for your generous donation.

Receipt Number: {donation_data.get('receipt_number', '')}
Date: {donation_data.get('date', '')}
Amount: ₹{donation_data.get('amount', 0):,.2f}
Category: {donation_data.get('category', '')}

Your donation receipt is attached.

With gratitude,
MandirMitra Temple Management
            """
            html_body = f"""
            <html>
            <body>
            <h2>Thank You for Your Donation</h2>
            <p>Dear {donation_data.get('devotee_name', 'Devotee')},</p>
            <p>Thank you for your generous donation.</p>
            <table>
            <tr><td><strong>Receipt Number:</strong></td><td>{donation_data.get('receipt_number', '')}</td></tr>
            <tr><td><strong>Date:</strong></td><td>{donation_data.get('date', '')}</td></tr>
            <tr><td><strong>Amount:</strong></td><td>₹{donation_data.get('amount', 0):,.2f}</td></tr>
            <tr><td><strong>Category:</strong></td><td>{donation_data.get('category', '')}</td></tr>
            </table>
            <p>Your donation receipt is attached.</p>
            <p>With gratitude,<br>MandirMitra Temple Management</p>
            </body>
            </html>
            """
            results["email"] = self.send_email(donation_data["email"], subject, body, html_body)

        return results

    def send_seva_booking_confirmation(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send seva booking confirmation via SMS and Email
        booking_data: {
            "devotee_name": str,
            "phone": str,
            "email": str,
            "receipt_number": str,
            "seva_name": str,
            "booking_date": str,
            "booking_time": str,
            "amount": float
        }
        """
        results = {"sms": None, "email": None}

        # SMS
        if booking_data.get("phone"):
            sms_message = (
                f"Dear {booking_data.get('devotee_name', 'Devotee')}, "
                f"Your {booking_data.get('seva_name', 'Seva')} booking is confirmed. "
                f"Date: {booking_data.get('booking_date', '')}, "
                f"Time: {booking_data.get('booking_time', '')}. "
                f"Receipt: {booking_data.get('receipt_number', '')}. "
                f"MandirMitra"
            )
            results["sms"] = self.send_sms(booking_data["phone"], sms_message)

        # Email
        if booking_data.get("email"):
            subject = f"Seva Booking Confirmation - {booking_data.get('receipt_number', '')}"
            body = f"""
Dear {booking_data.get('devotee_name', 'Devotee')},

Your seva booking has been confirmed.

Seva: {booking_data.get('seva_name', '')}
Date: {booking_data.get('booking_date', '')}
Time: {booking_data.get('booking_time', '')}
Amount: ₹{booking_data.get('amount', 0):,.2f}
Receipt Number: {booking_data.get('receipt_number', '')}

We look forward to your visit.

MandirMitra Temple Management
            """
            html_body = f"""
            <html>
            <body>
            <h2>Seva Booking Confirmed</h2>
            <p>Dear {booking_data.get('devotee_name', 'Devotee')},</p>
            <p>Your seva booking has been confirmed.</p>
            <table>
            <tr><td><strong>Seva:</strong></td><td>{booking_data.get('seva_name', '')}</td></tr>
            <tr><td><strong>Date:</strong></td><td>{booking_data.get('booking_date', '')}</td></tr>
            <tr><td><strong>Time:</strong></td><td>{booking_data.get('booking_time', '')}</td></tr>
            <tr><td><strong>Amount:</strong></td><td>₹{booking_data.get('amount', 0):,.2f}</td></tr>
            <tr><td><strong>Receipt:</strong></td><td>{booking_data.get('receipt_number', '')}</td></tr>
            </table>
            <p>We look forward to your visit.</p>
            <p>MandirMitra Temple Management</p>
            </body>
            </html>
            """
            results["email"] = self.send_email(booking_data["email"], subject, body, html_body)

        return results

    def send_seva_reminder(
        self, booking_data: Dict[str, Any], days_before: int = 1
    ) -> Dict[str, Any]:
        """Send seva booking reminder"""
        results = {"sms": None, "email": None}

        if booking_data.get("phone"):
            sms_message = (
                f"Reminder: Your {booking_data.get('seva_name', 'Seva')} is scheduled for "
                f"{booking_data.get('booking_date', '')} at {booking_data.get('booking_time', '')}. "
                f"MandirMitra"
            )
            results["sms"] = self.send_sms(booking_data["phone"], sms_message)

        if booking_data.get("email"):
            subject = f"Reminder: Seva Booking on {booking_data.get('booking_date', '')}"
            body = f"""
Dear {booking_data.get('devotee_name', 'Devotee')},

This is a reminder that your seva booking is scheduled for:

Seva: {booking_data.get('seva_name', '')}
Date: {booking_data.get('booking_date', '')}
Time: {booking_data.get('booking_time', '')}

We look forward to your visit.

MandirMitra Temple Management
            """
            results["email"] = self.send_email(booking_data["email"], subject, body)

        return results


# Singleton instance
notification_service = NotificationService()
