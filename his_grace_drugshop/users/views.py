from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta

from .models import User, OTP
from .serializers import (
    UserCreateSerializer, LoginSerializer, OTPSendSerializer,
    OTPVerifySerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
    UserSerializer
)
from .utils import send_email_otp, send_sms_otp, generate_otp


# ========================================================
# LANGUAGE CONFIGURATION ENDPOINT (FIXED: NOW ACCEPTS CHANGES)
# ========================================================
@api_view(['GET', 'PATCH'])
@csrf_exempt
@permission_classes([AllowAny])
def user_language_view(request):
    """
    Handles fetching and updating the application baseline language preferences.
    """
    if request.method == 'GET':
        # 🌟 Determine the user's active language choice (Fallback default to 'en')
        lang_code = 'en'
        if request.user and request.user.is_authenticated:
            # If your user model has a custom field tracking language choices:
            lang_code = getattr(request.user, 'language', 'en')

        return Response({
            'success': True,
            'data': {
                'success': True,
                'language_code': lang_code,
                'supported_languages': ['en', 'fr', 'es', 'ar', 'sw']
            }
        }, status=status.HTTP_200_OK)

    elif request.method == 'PATCH':
        # 🌟 Extract the runtime selection value from Flutter's payload body
        new_lang = request.data.get('language') or request.data.get('language_code')
        
        if not new_lang:
            return Response({
                'success': False,
                'error': 'Missing language parameters in payload.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Process mutations securely if the caller is an authenticated user session
        if request.user and request.user.is_authenticated:
            if hasattr(request.user, 'language'):
                request.user.language = new_lang
                request.user.save()

        return Response({
            'success': True,
            'data': {
                'success': True,
                'language_code': new_lang,
                'message': 'Language configuration altered successfully.'
            }
        }, status=status.HTTP_200_OK)


# =========================
# REGISTER
# =========================
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def register(request):
    print("Register endpoint hit")
    serializer = UserCreateSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        otp_code = generate_otp()
        OTP.objects.create(
            user=user,
            otp_code=otp_code,
            otp_type='email',
            destination=user.email,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        try:
            send_email_otp(user.email, otp_code, 'verification')
        except Exception as e:
            print(f"Email sending error: {e}")

        return Response({
            'success': True,
            'data': {
                'success': True,
                'message': 'Registration successful. Please verify your email.',
                'user': UserSerializer(user).data
            }
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'error': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# =========================
# LOGIN
# =========================
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def login_view(request):
    print("Login endpoint hit")
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data
        login(request, user)

        if not user.is_email_verified:
            return Response({
                'success': True, # Request handled successfully
                'data': {
                    'success': False,
                    'requires_verification': True,
                    'email': user.email,
                    'error': 'Please verify your email before logging in.'
                }
            }, status=status.HTTP_200_OK)

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'success': True,
            'data': {
                'success': True,
                'message': 'Login successful',
                'token': token.key,
                'user': UserSerializer(user).data
            }
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'error': 'Invalid validation parameters'
    }, status=status.HTTP_400_BAD_REQUEST)


# =========================
# SEND OTP
# =========================
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def send_otp(request):
    serializer = OTPSendSerializer(data=request.data)

    if serializer.is_valid():
        otp_type = serializer.validated_data['otp_type']
        email = serializer.validated_data.get('email')
        phone = serializer.validated_data.get('phone')

        user = None
        destination = email or phone

        try:
            if email:
                user = User.objects.get(email=email)
            elif phone:
                user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({
                'success': True,
                'data': {'success': False, 'error': 'Target entity user not found'}
            }, status=status.HTTP_200_OK)

        otp_code = generate_otp()

        OTP.objects.create(
            user=user,
            otp_code=otp_code,
            otp_type=otp_type,
            destination=destination,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        if email:
            send_email_otp(email, otp_code, otp_type)
        elif phone:
            send_sms_otp(phone, otp_code, otp_type)

        return Response({
            'success': True,
            'data': {
                'success': True,
                'message': f'OTP sent to {destination}'
            }
        })

    return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# VERIFY OTP
# =========================
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = OTPVerifySerializer(data=request.data)

    if serializer.is_valid():
        otp_code = serializer.validated_data['otp']
        otp_type = serializer.validated_data['otp_type']
        email = serializer.validated_data.get('email')
        phone = serializer.validated_data.get('phone')

        try:
            user = None
            if email:
                user = User.objects.get(email=email)
            elif phone:
                user = User.objects.get(phone=phone)

            if otp_type == 'email' and user.is_email_verified:
                return Response({
                    'success': True,
                    'data': {'success': True, 'message': 'Email already verified'}
                })
            elif otp_type == 'phone' and user.is_phone_verified:
                return Response({
                    'success': True,
                    'data': {'success': True, 'message': 'Phone already verified'}
                })

            otp = OTP.objects.get(
                user=user,
                otp_code=otp_code,
                otp_type=otp_type,
                is_used=False
            )

            if otp.expires_at < timezone.now():
                return Response({
                    'success': True,
                    'data': {'success': False, 'error': 'OTP expired'}
                })

            otp.is_used = True
            otp.save()

            if otp_type == 'email':
                user.is_email_verified = True
                user.save()
            elif otp_type == 'phone':
                user.is_phone_verified = True
                user.save()

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'success': True,
                'data': {
                    'success': True,
                    'message': 'OTP verified successfully',
                    'token': token.key,
                    'user': UserSerializer(user).data
                }
            })

        except User.DoesNotExist:
            return Response({'success': True, 'data': {'success': False, 'error': 'User not found'}})
        except OTP.DoesNotExist:
            return Response({'success': True, 'data': {'success': False, 'error': 'Invalid or expired OTP code'}})

    return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# FORGOT PASSWORD
# =========================
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': True,
                'data': {'success': False, 'error': 'No account associated with this email.'}
            })

        otp_code = generate_otp()
        OTP.objects.create(
            user=user,
            otp_code=otp_code,
            otp_type='reset',
            destination=email,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        send_email_otp(email, otp_code, 'reset')

        return Response({
            'success': True,
            'data': {
                'success': True,
                'message': 'Reset OTP sent'
            }
        })

    return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# RESET PASSWORD
# =========================
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.get(
                user=user,
                otp_code=otp_code,
                otp_type='reset',
                is_used=False
            )

            if otp.expires_at < timezone.now():
                return Response({
                    'success': True,
                    'data': {'success': False, 'error': 'OTP expired'}
                })

            otp.is_used = True
            otp.save()

            user.set_password(new_password)
            user.save()

            return Response({
                'success': True,
                'data': {
                    'success': True,
                    'message': 'Password reset successful'
                }
            })
        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({
                'success': True,
                'data': {'success': False, 'error': 'Invalid credentials or OTP sequence'}
            })

    return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# CURRENT USER
# =========================
@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_current_user(request):
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'data': serializer.data
    })


# =========================
# LOGOUT
# =========================
@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass

    return Response({
        'success': True,
        'data': {
            'success': True,
            'message': 'Logged out successfully'
        }
    })