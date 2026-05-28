# his_grace_drugshop/users/views.py

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


# =========================
# REGISTER
# =========================
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def register(request):
    print("Register endpoint hit")
    print("Request data:", request.data)

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
            'message': 'Registration successful. Please verify your email.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    print("Validation errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# LOGIN
# =========================
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def login_view(request):
    print("Login endpoint hit")
    print("Request data:", request.data)

    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data
        login(request, user)

        if not user.is_email_verified:
            return Response({
                'success': False,
                'error': 'Please verify your email before logging in.',
                'requires_verification': True,
                'email': user.email
            }, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'success': True,
            'message': 'Login successful',
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        if email:
            user = User.objects.get(email=email)
        elif phone:
            user = User.objects.get(phone=phone)

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
            'message': f'OTP sent to {destination}'
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# VERIFY OTP (FIXED - Handles duplicate requests)
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

            # Check if already verified
            if otp_type == 'email' and user.is_email_verified:
                return Response({
                    'success': True,
                    'message': 'Email already verified'
                })
            elif otp_type == 'phone' and user.is_phone_verified:
                return Response({
                    'success': True,
                    'message': 'Phone already verified'
                })

            # Try to find valid OTP
            otp = OTP.objects.get(
                user=user,
                otp_code=otp_code,
                otp_type=otp_type,
                is_used=False
            )

            # Check expiration
            if otp.expires_at < timezone.now():
                return Response({'error': 'OTP expired'}, status=400)

            # Mark as used and verify user
            otp.is_used = True
            otp.save()

            if otp_type == 'email':
                user.is_email_verified = True
                user.save()
            elif otp_type == 'phone':
                user.is_phone_verified = True
                user.save()

            return Response({
                'success': True,
                'message': 'OTP verified successfully'
            })

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid or expired OTP code'}, status=400)

    return Response(serializer.errors, status=400)


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

        user = User.objects.get(email=email)

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
            'message': 'Reset OTP sent'
        })

    return Response(serializer.errors, status=400)


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

        user = User.objects.get(email=email)

        otp = OTP.objects.get(
            user=user,
            otp_code=otp_code,
            otp_type='reset',
            is_used=False
        )

        if otp.expires_at < timezone.now():
            return Response({'error': 'OTP expired'}, status=400)

        otp.is_used = True
        otp.save()

        user.set_password(new_password)
        user.save()

        return Response({'success': True, 'message': 'Password reset successful'})

    return Response(serializer.errors, status=400)


# =========================
# CURRENT USER
# =========================
@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# =========================
# LOGOUT (FIXED)
# =========================
@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except:
        pass

    return Response({
        'success': True,
        'message': 'Logged out successfully'
    })