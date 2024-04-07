from django.http import Http404
from rest_framework import status
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
    def get(self, request: Request, pk=None) -> Response:
        if pk is not None:
            account = self.get_by_id(pk)
            serializer = AccountSerializer(account)
            return Response(serializer.data)
        
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

class AccountDetailView(APIView):
    @extend_schema(
        responses={200: AccountSerializer()},
        summary="Get account by ID",
        description="Retrieves an account by its ID."
    )
    def get(self, request: Request, pk: int) -> Response:
        try:
            account = Account.objects.get(pk=pk)
            serializer = AccountSerializer(account)
            return Response(serializer.data)
        except Account.DoesNotExist:
            raise Http404
    
    @extend_schema(
        responses={204: "No content"},
        summary="Delete account by ID",
        description="Deletes an account by its ID."
    )
    def delete(self, request: Request, pk: int) -> Response:
        try:
            account = Account.objects.get(pk=pk)
            account.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Account.DoesNotExist:
            raise Http404