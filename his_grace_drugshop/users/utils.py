# utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from twilio.rest import Client
import random
import string

def send_email_otp(email, otp_code, otp_type='verification'):
    """Send OTP via email"""
    if otp_type == 'verification':
        subject = 'Verify Your Email - His Grace Drugshop'
        message = f'''
        Hello,
        
        Your verification code for His Grace Drugshop is: {otp_code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        His Grace Drugshop Team
        '''
    else:  # password reset
        subject = 'Password Reset OTP - His Grace Drugshop'
        message = f'''
        Hello,
        
        Your password reset OTP is: {otp_code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        His Grace Drugshop Team
        '''
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def send_sms_otp(phone_number, otp_code, otp_type='verification'):
    """Send OTP via SMS using Twilio"""
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        if otp_type == 'verification':
            message_body = f'Your His Grace Drugshop verification code is: {otp_code}'
        else:
            message_body = f'Your His Grace Drugshop password reset code is: {otp_code}'
        
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return False

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

# ============================================
# NEW FUNCTIONS FOR EMAIL VERIFICATION LINK
# ============================================

def generate_email_verification_token(user):
    """Generate token for email verification"""
    return default_token_generator.make_token(user)

def generate_email_verification_link(user, request):
    """Generate verification link with token"""
    token = generate_email_verification_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Get the origin from request or use default
    origin = request.headers.get('Origin', getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000'))
    verification_link = f"{origin}/verify-email/{uid}/{token}/"
    
    return verification_link

def send_verification_link_email(user, request):
    """Send verification link email instead of OTP"""
    verification_link = generate_email_verification_link(user, request)
    
    subject = "Verify Your Email - His Grace Drugshop"
    plain_message = f"""
    Welcome to His Grace Drugshop!
    
    Please click this link to verify your email address and log in automatically:
    
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, please ignore this email.
    
    Best regards,
    His Grace Drugshop Team
    """
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .button {{
                display: inline-block;
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 20px 0;
                cursor: pointer;
                border-radius: 4px;
            }}
            .button:hover {{
                background-color: #45a049;
            }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>His Grace Drugshop</h2>
            </div>
            <div class="content">
                <h3>Welcome {user.get_full_name() or user.username}!</h3>
                <p>Thank you for registering with His Grace Drugshop.</p>
                <p>Please click the button below to verify your email address and log in automatically:</p>
                <a href="{verification_link}" class="button">Verify Email & Login</a>
                <p>Or copy and paste this link into your browser:</p>
                <p style="background-color: #e9ecef; padding: 10px; border-radius: 4px; word-break: break-all;">
                    {verification_link}
                </p>
                <p><strong>This link will expire in 24 hours.</strong></p>
                <p>If you didn't create an account, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2025 His Grace Drugshop. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

def verify_email_token(uidb64, token):
    """Verify email token and return user if valid"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        from .models import User
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            return user
        return None
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None