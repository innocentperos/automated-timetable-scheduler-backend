from django.db import models
from django.contrib.auth.models import User
from core.models import Department

# Create your models here.

USER_STAFF = "staff"
USER_STUDENT = "student"
USER_ADMIN = "admin"


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    user_type = models.CharField(
        max_length=25,
        choices=(
            (USER_ADMIN, "Admin"),
            (USER_STAFF, "Staff"),
            (USER_STUDENT, "Student"),
        ),
    )

    level = models.IntegerField(
        choices=(
            (100, "100L"),
            (200, "200L"),
            (300, "300L"),
            (400, "400L"),
            (500, "500L"),
            (None, "Not a student"),
        ),
        null=True,
        blank=True,
        default=None,
    )

    department = models.ForeignKey(
        Department,
        null=True,
        default=None,
        on_delete=models.CASCADE,
        related_name="accounts",
    )

    def name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def email(self):
        return self.user.email
    
