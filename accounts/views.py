from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView, Request, Response
from .models import Account
from .serializers import AccountSerializer, LoginSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema

class LoginView(TokenObtainPairView):
    ...

class SecondLoginView(APIView):
    @extend_schema(
        request=TokenObtainPairSerializer,
        responses={200: TokenObtainPairSerializer()},
        summary="Second login",
        description="Performs a second login to obtain JWT tokens."
    )
    def post(self, request: Request) -> Response:
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

class FirstLoginView(APIView):
    @extend_schema(
        request=LoginSerializer,
        responses={200: TokenObtainPairSerializer()},
        summary="First login",
        description="Performs a first login to obtain JWT tokens."
    )
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.validated_data)
        if not user:
            return Response(
                {"detail": "No active account was found."},
                status.HTTP_403_FORBIDDEN,
            )
        refresh = RefreshToken.for_user(user)
        token_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(token_data)

class AccountView(APIView):
    @extend_schema(
        responses={200: AccountSerializer(many=True)},
        summary="List accounts",
        description="Returns a list of all accounts."
    )
    def get(self, request: Request) -> Response:
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=AccountSerializer,
        responses={201: AccountSerializer()},
        summary="Create account",
        description="Creates a new account."
    )
    def post(self, request: Request) -> Response:
        serializer = AccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
