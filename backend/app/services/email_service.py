"""
Email notification service for user communications
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings


class EmailService:
    """Email notification service using SMTP"""

    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
        """Send email via SMTP"""
        if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print(f"Email skipped (SMTP not configured): {subject} to {to_email}")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Attach both text and HTML versions
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            print(f"Email sent successfully: {subject} to {to_email}")
            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    @staticmethod
    def send_welcome_email(email: str, full_name: Optional[str] = None):
        """Send welcome email to new users"""
        name = full_name or email.split('@')[0]

        subject = "Welcome to BiliNote! 🎉"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 32px;">Welcome to BiliNote!</h1>
            </div>

            <div style="background: #ffffff; padding: 40px 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
                <p style="font-size: 18px; margin-bottom: 20px;">Hi {name},</p>

                <p style="margin-bottom: 20px;">
                    Thank you for joining BiliNote! We're excited to help you transform videos into structured notes with the power of AI.
                </p>

                <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <h2 style="margin-top: 0; color: #667eea; font-size: 20px;">🎁 Your Free Plan Includes:</h2>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>5 videos per month</li>
                        <li>Up to 10 minutes per video</li>
                        <li>AI-powered note generation</li>
                        <li>Multiple export formats</li>
                    </ul>
                </div>

                <h3 style="color: #667eea; margin-top: 30px;">Get Started:</h3>
                <ol style="margin: 10px 0; padding-left: 20px;">
                    <li>Go to your <a href="{settings.FRONTEND_URL}/dashboard" style="color: #667eea; text-decoration: none;">Dashboard</a></li>
                    <li>Click "Generate Note"</li>
                    <li>Paste a video URL</li>
                    <li>Let AI do the magic! ✨</li>
                </ol>

                <div style="text-align: center; margin: 40px 0;">
                    <a href="{settings.FRONTEND_URL}/dashboard" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 40px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px;">Go to Dashboard</a>
                </div>

                <p style="margin-top: 30px; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; padding-top: 20px;">
                    Need help? Reply to this email or visit our <a href="{settings.FRONTEND_URL}/help" style="color: #667eea;">Help Center</a>.
                </p>
            </div>

            <div style="text-align: center; margin-top: 20px; color: #9ca3af; font-size: 12px;">
                <p>BiliNote - AI-Powered Video Notes</p>
                <p>This email was sent to {email}</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to BiliNote!

        Hi {name},

        Thank you for joining BiliNote! We're excited to help you transform videos into structured notes with the power of AI.

        Your Free Plan Includes:
        - 5 videos per month
        - Up to 10 minutes per video
        - AI-powered note generation
        - Multiple export formats

        Get Started:
        1. Go to your Dashboard: {settings.FRONTEND_URL}/dashboard
        2. Click "Generate Note"
        3. Paste a video URL
        4. Let AI do the magic!

        Need help? Reply to this email or visit our Help Center.

        Best regards,
        The BiliNote Team
        """

        return EmailService._send_email(email, subject, html_content, text_content)

    @staticmethod
    def send_payment_success_email(email: str, plan_name: str, amount: float, billing_cycle: str):
        """Send payment success notification"""

        subject = f"Payment Confirmed - {plan_name} Plan"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #10b981; padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 32px;">✓ Payment Successful!</h1>
            </div>

            <div style="background: #ffffff; padding: 40px 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
                <p style="font-size: 18px; margin-bottom: 20px;">Thank you for your payment!</p>

                <p style="margin-bottom: 20px;">
                    Your subscription to the <strong>{plan_name}</strong> plan has been activated.
                </p>

                <div style="background: #f0fdf4; padding: 25px; border-radius: 8px; margin: 30px 0; border-left: 4px solid #10b981;">
                    <h3 style="margin-top: 0; color: #059669;">Payment Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280;">Plan:</td>
                            <td style="padding: 8px 0; text-align: right; font-weight: 600;">{plan_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280;">Billing:</td>
                            <td style="padding: 8px 0; text-align: right; font-weight: 600;">{billing_cycle.capitalize()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280;">Amount:</td>
                            <td style="padding: 8px 0; text-align: right; font-weight: 600; font-size: 18px; color: #059669;">${amount:.2f}</td>
                        </tr>
                    </table>
                </div>

                <p style="margin-bottom: 20px;">
                    You can now enjoy all the benefits of your {plan_name} subscription!
                </p>

                <div style="text-align: center; margin: 40px 0;">
                    <a href="{settings.FRONTEND_URL}/dashboard" style="display: inline-block; background: #10b981; color: white; padding: 14px 40px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; margin-right: 10px;">Go to Dashboard</a>
                    <a href="{settings.FRONTEND_URL}/dashboard/settings/billing" style="display: inline-block; background: white; color: #10b981; border: 2px solid #10b981; padding: 12px 40px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px;">View Invoice</a>
                </div>

                <p style="margin-top: 30px; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; padding-top: 20px;">
                    Questions about your subscription? Visit your <a href="{settings.FRONTEND_URL}/dashboard/settings/billing" style="color: #10b981;">billing settings</a>.
                </p>
            </div>

            <div style="text-align: center; margin-top: 20px; color: #9ca3af; font-size: 12px;">
                <p>BiliNote - AI-Powered Video Notes</p>
                <p>This email was sent to {email}</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Payment Successful!

        Thank you for your payment!

        Your subscription to the {plan_name} plan has been activated.

        Payment Details:
        - Plan: {plan_name}
        - Billing: {billing_cycle.capitalize()}
        - Amount: ${amount:.2f}

        You can now enjoy all the benefits of your {plan_name} subscription!

        Go to Dashboard: {settings.FRONTEND_URL}/dashboard
        View Invoice: {settings.FRONTEND_URL}/dashboard/settings/billing

        Questions about your subscription? Visit your billing settings.

        Best regards,
        The BiliNote Team
        """

        return EmailService._send_email(email, subject, html_content, text_content)

    @staticmethod
    def send_payment_failed_email(email: str, plan_name: str):
        """Send payment failed notification"""

        subject = "Payment Failed - Action Required"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #ef4444; padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 32px;">⚠️ Payment Failed</h1>
            </div>

            <div style="background: #ffffff; padding: 40px 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
                <p style="font-size: 18px; margin-bottom: 20px;">We couldn't process your payment</p>

                <p style="margin-bottom: 20px;">
                    Your recent payment for the <strong>{plan_name}</strong> plan was unsuccessful.
                </p>

                <div style="background: #fef2f2; padding: 25px; border-radius: 8px; margin: 30px 0; border-left: 4px solid #ef4444;">
                    <h3 style="margin-top: 0; color: #dc2626;">What happens now?</h3>
                    <ul style="margin: 10px 0; padding-left: 20px; color: #6b7280;">
                        <li>Your subscription is now <strong>Past Due</strong></li>
                        <li>You still have access for a limited time</li>
                        <li>Please update your payment method to continue</li>
                    </ul>
                </div>

                <p style="margin-bottom: 20px;">
                    Common reasons for payment failure:
                </p>
                <ul style="margin: 10px 0 30px 0; padding-left: 20px; color: #6b7280;">
                    <li>Insufficient funds</li>
                    <li>Expired credit card</li>
                    <li>Incorrect billing information</li>
                    <li>Card issuer declined the transaction</li>
                </ul>

                <div style="text-align: center; margin: 40px 0;">
                    <a href="{settings.FRONTEND_URL}/dashboard/settings/billing" style="display: inline-block; background: #ef4444; color: white; padding: 14px 40px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px;">Update Payment Method</a>
                </div>

                <p style="margin-top: 30px; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; padding-top: 20px;">
                    Need help? Contact our support team at support@bilinote.app
                </p>
            </div>

            <div style="text-align: center; margin-top: 20px; color: #9ca3af; font-size: 12px;">
                <p>BiliNote - AI-Powered Video Notes</p>
                <p>This email was sent to {email}</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Payment Failed - Action Required

        We couldn't process your payment

        Your recent payment for the {plan_name} plan was unsuccessful.

        What happens now?
        - Your subscription is now Past Due
        - You still have access for a limited time
        - Please update your payment method to continue

        Common reasons for payment failure:
        - Insufficient funds
        - Expired credit card
        - Incorrect billing information
        - Card issuer declined the transaction

        Update Payment Method: {settings.FRONTEND_URL}/dashboard/settings/billing

        Need help? Contact our support team at support@bilinote.app

        Best regards,
        The BiliNote Team
        """

        return EmailService._send_email(email, subject, html_content, text_content)

    @staticmethod
    def send_subscription_cancelled_email(email: str, plan_name: str, access_until: str):
        """Send subscription cancellation confirmation"""

        subject = "Subscription Cancelled"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #6b7280; padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 32px;">Subscription Cancelled</h1>
            </div>

            <div style="background: #ffffff; padding: 40px 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
                <p style="font-size: 18px; margin-bottom: 20px;">We're sorry to see you go!</p>

                <p style="margin-bottom: 20px;">
                    Your <strong>{plan_name}</strong> subscription has been cancelled.
                </p>

                <div style="background: #f9fafb; padding: 25px; border-radius: 8px; margin: 30px 0; border-left: 4px solid #6b7280;">
                    <h3 style="margin-top: 0; color: #374151;">Important Information</h3>
                    <p style="margin: 10px 0; color: #6b7280;">
                        You'll continue to have access to your {plan_name} features until:
                    </p>
                    <p style="margin: 10px 0; font-size: 20px; font-weight: 600; color: #374151;">
                        {access_until}
                    </p>
                    <p style="margin: 10px 0; color: #6b7280;">
                        After this date, you'll be moved to our Free plan.
                    </p>
                </div>

                <p style="margin-bottom: 20px;">
                    You can reactivate your subscription at any time from your billing settings.
                </p>

                <div style="text-align: center; margin: 40px 0;">
                    <a href="{settings.FRONTEND_URL}/dashboard/settings/billing" style="display: inline-block; background: #6b7280; color: white; padding: 14px 40px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px;">View Billing Settings</a>
                </div>

                <p style="margin-top: 30px; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; padding-top: 20px;">
                    We'd love to hear your feedback. What could we have done better? Reply to this email to let us know.
                </p>
            </div>

            <div style="text-align: center; margin-top: 20px; color: #9ca3af; font-size: 12px;">
                <p>BiliNote - AI-Powered Video Notes</p>
                <p>This email was sent to {email}</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Subscription Cancelled

        We're sorry to see you go!

        Your {plan_name} subscription has been cancelled.

        Important Information:
        You'll continue to have access to your {plan_name} features until: {access_until}

        After this date, you'll be moved to our Free plan.

        You can reactivate your subscription at any time from your billing settings.

        View Billing Settings: {settings.FRONTEND_URL}/dashboard/settings/billing

        We'd love to hear your feedback. What could we have done better? Reply to this email to let us know.

        Best regards,
        The BiliNote Team
        """

        return EmailService._send_email(email, subject, html_content, text_content)
