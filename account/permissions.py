from rest_framework.permissions import BasePermission
from django.contrib.auth.models import User
from rest_framework.request import Request
from .models import Account, USER_ADMIN, USER_STUDENT, USER_STAFF


class IsStudent(BasePermission):
    def has_permission(self, request: Request, view):
        user: User = request.user
        if user.is_anonymous:
            return False

        account: Account | None = user.account  # type: ignore
        if not account:
            return False

        return account.user_type == USER_STUDENT


class IsStaff(BasePermission):
    def has_permission(self, request: Request, view):
        user: User = request.user
        if user.is_anonymous:
            return False

        account: Account | None = user.account  # type: ignore
        if not account:
            return False

        return account.user_type == USER_STAFF

class IsAdmin(BasePermission):
    def has_permission(self, request: Request, view):
        user: User = request.user
        if user.is_anonymous:
            return False

        account: Account | None = user.account  # type: ignore
        if not account:
            return False

        return account.user_type == USER_ADMIN


def userIsAdmin(request: Request):
    user: User = request.user
    if user.is_anonymous:
        return False

    account: Account | None = user.account  # type: ignore
    if not account:
        return False

    return account.user_type == USER_ADMIN

def userIsStaff(request: Request):
    user: User = request.user
    if user.is_anonymous:
        return False

    account: Account | None = user.account  # type: ignore
    if not account:
        return False

    return account.user_type == USER_STAFF


def userIsStudent(request: Request):
    user: User = request.user
    if user.is_anonymous:
        return False

    account: Account | None = user.account  # type: ignore
    if not account:
        return False

    return account.user_type == USER_STUDENT
