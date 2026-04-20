from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken as SimpleJWTRefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CustomUser, RefreshToken, Role
from .serializers import (
    RegisterSerializer, LoginSerializer, TokenSerializer,
    UserSerializer, RefreshTokenSerializer, PasswordChangeSerializer
)
from decouple import config


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = SimpleJWTRefreshToken.for_user(user)
            refresh['role'] = user.role_name
            refresh['email'] = user.email

            # Store refresh token
            expire_days = config('JWT_REFRESH_TOKEN_EXPIRE_DAYS', default=7, cast=int)
            RefreshToken.objects.create(
                user=user,
                token=str(refresh),
                expires_at=timezone.now() + timedelta(days=expire_days)
            )

            return Response({
                'message': 'User registered successfully.',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = SimpleJWTRefreshToken.for_user(user)
            refresh['role'] = user.role_name
            refresh['email'] = user.email

            expire_days = config('JWT_REFRESH_TOKEN_EXPIRE_DAYS', default=7, cast=int)
            # Revoke old tokens
            RefreshToken.objects.filter(user=user, is_revoked=False).update(is_revoked=True)
            # Store new token
            RefreshToken.objects.create(
                user=user,
                token=str(refresh),
                expires_at=timezone.now() + timedelta(days=expire_days)
            )

            return Response({
                'message': 'Login successful.',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                # Blacklist via simplejwt
                token = SimpleJWTRefreshToken(refresh_token)
                token.blacklist()
                # Mark as revoked in our DB
                RefreshToken.objects.filter(token=refresh_token).update(is_revoked=True)
            return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token_str = serializer.validated_data['refresh']

                # Check if revoked in our DB
                db_token = RefreshToken.objects.filter(token=refresh_token_str).first()
                if db_token and not db_token.is_valid:
                    return Response({'error': 'Refresh token is expired or revoked.'}, status=status.HTTP_401_UNAUTHORIZED)

                refresh = SimpleJWTRefreshToken(refresh_token_str)
                user_id = refresh.payload.get('user_id')
                user = CustomUser.objects.get(id=user_id)

                # Attach role to new token
                refresh['role'] = user.role_name
                refresh['email'] = user.email

                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }, status=status.HTTP_200_OK)
            except (TokenError, InvalidToken) as e:
                return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenVerifyView(APIView):
    """Used by gateway to validate tokens and get user info."""
    permission_classes = [AllowAny]

    def post(self, request):
        token_str = request.data.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token_str:
            return Response({'valid': False, 'error': 'No token provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token_str)
            user_id = validated_token.get('user_id')
            user = CustomUser.objects.get(id=user_id)

            return Response({
                'valid': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role_name,
                    'is_active': user.is_active,
                }
            }, status=status.HTTP_200_OK)
        except (TokenError, InvalidToken) as e:
            return Response({'valid': False, 'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except CustomUser.DoesNotExist:
            return Response({'valid': False, 'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        from apps.authentication.permissions import IsAdminUser as CustomIsAdmin
        return [CustomIsAdmin()]


class RoleListView(APIView):
    """GET /auth/roles/ — list all roles (admin only)."""

    def get_permissions(self):
        from apps.authentication.permissions import IsAdminUser as CustomIsAdmin
        return [CustomIsAdmin()]

    def get(self, request):
        roles = Role.objects.all().values('id', 'name', 'description')
        return Response(list(roles))

    def post(self, request):
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '')
        if not name:
            return Response({'error': 'name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        role, created = Role.objects.get_or_create(name=name, defaults={'description': description})
        return Response(
            {'id': role.id, 'name': role.name, 'description': role.description, 'created': created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class AssignRoleView(APIView):
    """POST /auth/users/{id}/assign-role/ — change a user's role_name (admin only)."""

    def get_permissions(self):
        from apps.authentication.permissions import IsAdminUser as CustomIsAdmin
        return [CustomIsAdmin()]

    def post(self, request, pk):
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_role = request.data.get('role', '').strip()
        valid_roles = [choice[0] for choice in CustomUser.ROLE_CHOICES]
        if new_role not in valid_roles:
            return Response(
                {'error': f'Invalid role. Choose from: {valid_roles}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.role_name = new_role
        user.save(update_fields=['role_name'])
        return Response({
            'message': f"Role updated to '{new_role}' for user {user.email}.",
            'user': UserSerializer(user).data,
        })
