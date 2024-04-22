from rest_framework import serializers

from account.models import Account


class AccountSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = Account
        fields = ("user", "pk", "name", "email", "user_type", "department", "level")
