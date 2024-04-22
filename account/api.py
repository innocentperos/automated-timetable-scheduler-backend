from account.forms import LoginForm, RegisterForm
from account.serializer import AccountSerializer
from .models import User, Account
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import IntegrityError, transaction


class AccountViewset(ViewSet):
    permission_classes = (AllowAny,)

    @action(methods=("POST",), detail=False)
    def login(self, request: Request):
        form = LoginForm(request.data)  # type: ignore

        if not form.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "Invalid form provided", "errors": form.errors},
            )

        form_data = form.cleaned_data
        try:
            user = User.objects.get(email=form_data["email"])

            if not user.check_password(form_data["password"]):
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={"details": "Wrong password provided"},
                )

            (token, _) = Token.objects.get_or_create(user=user)
            return Response(
                data={
                    "details": "Login successfully",
                    "token": token.key,
                    "account": AccountSerializer(user.account).data,  # type: ignore
                }
            )
        except User.DoesNotExist:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"details": "No account found"},
            )

        pass

    @action(methods=("POST",), detail=False)
    def register(self, request: Request):
        form = RegisterForm(request.data)  # type: ignore

        if not form.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "Invalid form provided", "errors": form.errors},
            )

        data = form.cleaned_data

        account = Account(department=data["department"], user_type=data["user_type"])

        user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            username=data["email"],
        )
        user.set_password(data["password"])

        if data["user_type"] == RegisterForm.STUDENT_USER_TYPE:
            if not data["level"]:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "details": "Invalid form provided",
                        "errors": {"level": ["Level missing for student account type"]},
                    },
                )

            account.level = data["level"]

        try:
            with transaction.atomic():
                user.save()
                account.user = user
                account.save()

                (token, _) = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        "details": "Registration was successful",
                        "token": token.key,
                        "account": AccountSerializer(account).data,
                    }
                )
        except IntegrityError as e:
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"details": "Email address already used", "errors": str(e)},
            )

    @action(methods=("POST",), detail=False, permission_classes=(IsAuthenticated,))
    def logout(self, request: Request):
        user: User = request.user

        try:
            token = Token.objects.get(user=user)
            token.delete()
        except Token.DoesNotExist:
            pass

        return Response({"details": "Logout was successful"})

    @action(methods=("POST",), detail=False)
    def check_email(self, request: Request):
        email = request.data.get("email", None)  # type: ignore

        if not email:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "Email address not provided"},
            )

        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"details": "No user found"}
            )

        return Response({"details": "Email found"})
